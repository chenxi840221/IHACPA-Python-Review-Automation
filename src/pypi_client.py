#!/usr/bin/env python3
"""
PyPI API Client for IHACPA Python Package Review Automation
Handles PyPI API interactions to fetch package information
"""

import requests
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from urllib.parse import urljoin


class PyPIClient:
    """Client for interacting with PyPI API"""
    
    BASE_URL = "https://pypi.org/pypi/"
    JSON_SUFFIX = "/json"
    
    def __init__(self, timeout: int = 10, max_retries: int = 3):
        """Initialize PyPI client with configuration"""
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = None
        self.logger = logging.getLogger(__name__)
        
    def _make_request(self, url: str) -> Optional[Dict[str, Any]]:
        """Make synchronous HTTP request to PyPI API"""
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()
                
                data = response.json()
                self.logger.debug(f"Successfully fetched data from {url}")
                return data
                
            except requests.exceptions.Timeout:
                self.logger.warning(f"Timeout on attempt {attempt + 1} for {url}")
                if attempt == self.max_retries - 1:
                    self.logger.error(f"Max retries exceeded for {url}")
                    
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    self.logger.warning(f"Package not found: {url}")
                    return None
                else:
                    self.logger.error(f"HTTP error {e.response.status_code} for {url}")
                    if attempt == self.max_retries - 1:
                        return None
                        
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Request error on attempt {attempt + 1} for {url}: {e}")
                if attempt == self.max_retries - 1:
                    return None
                    
            except Exception as e:
                self.logger.error(f"Unexpected error for {url}: {e}")
                return None
                
            if attempt < self.max_retries - 1:
                await_time = 2 ** attempt  # Exponential backoff
                self.logger.debug(f"Waiting {await_time} seconds before retry")
                import time
                time.sleep(await_time)
                
        return None
    
    def get_package_info(self, package_name: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive package information from PyPI"""
        url = f"{self.BASE_URL}{package_name}{self.JSON_SUFFIX}"
        data = self._make_request(url)
        
        if not data:
            return None
            
        try:
            info = data.get('info', {})
            releases = data.get('releases', {})
            
            # Get latest version
            latest_version = info.get('version', '')
            
            # Get latest release date
            latest_release_date = None
            if latest_version and latest_version in releases:
                release_files = releases[latest_version]
                if release_files:
                    upload_time = release_files[0].get('upload_time_iso_8601', '')
                    if upload_time:
                        try:
                            latest_release_date = datetime.fromisoformat(upload_time.replace('Z', '+00:00'))
                        except ValueError:
                            self.logger.warning(f"Could not parse date: {upload_time}")
            
            # Get GitHub URL from project URLs
            github_url = None
            project_urls = info.get('project_urls', {})
            if project_urls:
                for key, url in project_urls.items():
                    if 'github' in key.lower() or 'github.com' in str(url).lower():
                        github_url = url
                        break
            
            # If no GitHub URL found, check homepage
            if not github_url:
                homepage = info.get('home_page', '')
                if 'github.com' in homepage.lower():
                    github_url = homepage
            
            # Get dependencies
            requires_dist = info.get('requires_dist', [])
            dependencies = []
            if requires_dist:
                for req in requires_dist:
                    if isinstance(req, str):
                        # Extract package name (before any version specifiers)
                        dep_name = req.split('(')[0].split('[')[0].split(';')[0].split('=')[0].split('<')[0].split('>')[0].strip()
                        if dep_name:
                            dependencies.append(dep_name)
            
            package_info = {
                'name': info.get('name', package_name),
                'version': latest_version,
                'summary': info.get('summary', ''),
                'description': info.get('description', ''),
                'author': info.get('author', ''),
                'author_email': info.get('author_email', ''),
                'maintainer': info.get('maintainer', ''),
                'maintainer_email': info.get('maintainer_email', ''),
                'license': info.get('license', ''),
                'home_page': info.get('home_page', ''),
                'project_urls': project_urls,
                'github_url': github_url,
                'latest_version': latest_version,
                'latest_release_date': latest_release_date,
                'pypi_url': f"https://pypi.org/project/{package_name}/",
                'pypi_latest_url': f"https://pypi.org/project/{package_name}/{latest_version}/",
                'requires_dist': requires_dist,
                'dependencies': dependencies,
                'development_status': info.get('classifiers', []),
                'keywords': info.get('keywords', ''),
                'platform': info.get('platform', ''),
                'download_url': info.get('download_url', ''),
                'package_url': info.get('package_url', ''),
                'release_url': info.get('release_url', ''),
                'docs_url': info.get('docs_url', ''),
                'bugtrack_url': info.get('bugtrack_url', ''),
                'classifiers': info.get('classifiers', [])
            }
            
            return package_info
            
        except Exception as e:
            self.logger.error(f"Error parsing package info for {package_name}: {e}")
            return None
    
    def get_package_versions(self, package_name: str) -> List[str]:
        """Get all available versions for a package"""
        url = f"{self.BASE_URL}{package_name}{self.JSON_SUFFIX}"
        data = self._make_request(url)
        
        if not data:
            return []
            
        try:
            releases = data.get('releases', {})
            versions = list(releases.keys())
            return sorted(versions, reverse=True)  # Latest first
            
        except Exception as e:
            self.logger.error(f"Error getting versions for {package_name}: {e}")
            return []
    
    def get_version_info(self, package_name: str, version: str) -> Optional[Dict[str, Any]]:
        """Get information for a specific version"""
        url = f"{self.BASE_URL}{package_name}/{version}{self.JSON_SUFFIX}"
        data = self._make_request(url)
        
        if not data:
            return None
            
        try:
            info = data.get('info', {})
            
            # Get release date for this version
            releases = data.get('releases', {})
            release_date = None
            if version in releases:
                release_files = releases[version]
                if release_files:
                    upload_time = release_files[0].get('upload_time_iso_8601', '')
                    if upload_time:
                        try:
                            release_date = datetime.fromisoformat(upload_time.replace('Z', '+00:00'))
                        except ValueError:
                            self.logger.warning(f"Could not parse date: {upload_time}")
            
            version_info = {
                'name': info.get('name', package_name),
                'version': version,
                'release_date': release_date,
                'pypi_url': f"https://pypi.org/project/{package_name}/{version}/",
                'summary': info.get('summary', ''),
                'description': info.get('description', ''),
                'author': info.get('author', ''),
                'license': info.get('license', ''),
                'classifiers': info.get('classifiers', [])
            }
            
            return version_info
            
        except Exception as e:
            self.logger.error(f"Error getting version info for {package_name} {version}: {e}")
            return None
    
    def check_package_exists(self, package_name: str) -> bool:
        """Check if a package exists on PyPI"""
        url = f"{self.BASE_URL}{package_name}{self.JSON_SUFFIX}"
        data = self._make_request(url)
        return data is not None
    
    def get_development_status(self, package_name: str) -> str:
        """Extract development status from classifiers"""
        package_info = self.get_package_info(package_name)
        if not package_info:
            return "Unknown"
            
        classifiers = package_info.get('classifiers', [])
        for classifier in classifiers:
            if 'Development Status' in classifier:
                # Extract status like "4 - Beta" from "Development Status :: 4 - Beta"
                status = classifier.split('::')[-1].strip()
                return status
                
        return "Unknown"
    
    def compare_versions(self, current_version: str, latest_version: str) -> Dict[str, Any]:
        """Compare current and latest versions"""
        try:
            from packaging import version
            
            current_parsed = version.parse(current_version)
            latest_parsed = version.parse(latest_version)
            
            is_outdated = current_parsed < latest_parsed
            is_same = current_parsed == latest_parsed
            is_newer = current_parsed > latest_parsed
            
            return {
                'current_version': current_version,
                'latest_version': latest_version,
                'is_outdated': is_outdated,
                'is_same': is_same,
                'is_newer': is_newer,
                'needs_update': is_outdated,
                'version_gap': str(latest_parsed - current_parsed) if is_outdated else "0"
            }
            
        except ImportError:
            # Fallback to string comparison if packaging is not available
            is_outdated = current_version != latest_version
            return {
                'current_version': current_version,
                'latest_version': latest_version,
                'is_outdated': is_outdated,
                'is_same': current_version == latest_version,
                'is_newer': False,
                'needs_update': is_outdated,
                'version_gap': "unknown"
            }
        except Exception as e:
            self.logger.error(f"Error comparing versions {current_version} vs {latest_version}: {e}")
            return {
                'current_version': current_version,
                'latest_version': latest_version,
                'is_outdated': False,
                'is_same': False,
                'is_newer': False,
                'needs_update': False,
                'version_gap': "error"
            }
    
    async def get_package_info_async(self, package_name: str) -> Optional[Dict[str, Any]]:
        """Async version of get_package_info"""
        url = f"{self.BASE_URL}{package_name}{self.JSON_SUFFIX}"
        
        if not self.session:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        
        for attempt in range(self.max_retries):
            try:
                async with self.session.get(url) as response:
                    if response.status == 404:
                        self.logger.warning(f"Package not found: {package_name}")
                        return None
                    
                    response.raise_for_status()
                    data = await response.json()
                    
                    # Process the data same as sync version
                    return self._process_package_data(data, package_name)
                    
            except asyncio.TimeoutError:
                self.logger.warning(f"Timeout on attempt {attempt + 1} for {package_name}")
                if attempt == self.max_retries - 1:
                    self.logger.error(f"Max retries exceeded for {package_name}")
                    
            except aiohttp.ClientError as e:
                self.logger.error(f"HTTP error on attempt {attempt + 1} for {package_name}: {e}")
                if attempt == self.max_retries - 1:
                    return None
                    
            except Exception as e:
                self.logger.error(f"Unexpected error for {package_name}: {e}")
                return None
                
            if attempt < self.max_retries - 1:
                await_time = 2 ** attempt
                await asyncio.sleep(await_time)
                
        return None
    
    def _process_package_data(self, data: Dict[str, Any], package_name: str) -> Dict[str, Any]:
        """Process raw PyPI data into structured format"""
        info = data.get('info', {})
        releases = data.get('releases', {})
        
        # Get latest version
        latest_version = info.get('version', '')
        
        # Get latest release date
        latest_release_date = None
        if latest_version and latest_version in releases:
            release_files = releases[latest_version]
            if release_files:
                upload_time = release_files[0].get('upload_time_iso_8601', '')
                if upload_time:
                    try:
                        latest_release_date = datetime.fromisoformat(upload_time.replace('Z', '+00:00'))
                    except ValueError:
                        self.logger.warning(f"Could not parse date: {upload_time}")
        
        # Get GitHub URL
        github_url = None
        project_urls = info.get('project_urls', {})
        if project_urls:
            for key, url in project_urls.items():
                if 'github' in key.lower() or 'github.com' in str(url).lower():
                    github_url = url
                    break
        
        if not github_url:
            homepage = info.get('home_page', '')
            if 'github.com' in homepage.lower():
                github_url = homepage
        
        # Get dependencies
        requires_dist = info.get('requires_dist', [])
        dependencies = []
        if requires_dist:
            for req in requires_dist:
                if isinstance(req, str):
                    dep_name = req.split('(')[0].split('[')[0].split(';')[0].split('=')[0].split('<')[0].split('>')[0].strip()
                    if dep_name:
                        dependencies.append(dep_name)
        
        return {
            'name': info.get('name', package_name),
            'version': latest_version,
            'latest_version': latest_version,
            'latest_release_date': latest_release_date,
            'pypi_url': f"https://pypi.org/project/{package_name}/",
            'pypi_latest_url': f"https://pypi.org/project/{package_name}/{latest_version}/",
            'github_url': github_url,
            'dependencies': dependencies,
            'requires_dist': requires_dist,
            'development_status': info.get('classifiers', []),
            'summary': info.get('summary', ''),
            'author': info.get('author', ''),
            'license': info.get('license', ''),
            'classifiers': info.get('classifiers', [])
        }
    
    async def close(self):
        """Close async session"""
        if self.session:
            await self.session.close()
            self.session = None