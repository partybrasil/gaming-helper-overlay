"""
Assets Manager
Manages application assets including icons, sounds, animations, and backgrounds.
"""

import logging
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QPixmap, QIcon

from core.config_manager import ConfigManager


class AssetsManager(QObject):
    """Manages all application assets."""
    
    # Signals
    asset_added = Signal(str, str)  # category, asset_name
    asset_removed = Signal(str, str)  # category, asset_name
    asset_updated = Signal(str, str)  # category, asset_name
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        
        self.config_manager = config_manager
        self.logger = logging.getLogger("AssetsManager")
        
        # Asset directories
        self.assets_root = Path(__file__).parent.parent / "assets"
        self.icons_dir = self.assets_root / "icons"
        self.sounds_dir = self.assets_root / "sounds"
        self.animations_dir = self.assets_root / "animations"
        self.backgrounds_dir = self.assets_root / "backgrounds"
        
        # Ensure directories exist
        self._ensure_directories()
        
        # Asset cache
        self.asset_cache: Dict[str, QPixmap] = {}
        
        # Supported file formats
        self.supported_image_formats = ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.svg']
        self.supported_sound_formats = ['.wav', '.mp3', '.ogg', '.flac']
        self.supported_animation_formats = ['.gif', '.webp']
    
    def _ensure_directories(self):
        """Ensure all asset directories exist."""
        for directory in [self.icons_dir, self.sounds_dir, 
                         self.animations_dir, self.backgrounds_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_icon(self, name: str, cache: bool = True) -> Optional[QIcon]:
        """Get an icon by name."""
        icon_path = self.icons_dir / f"{name}.png"
        
        # Try different extensions if .png doesn't exist
        if not icon_path.exists():
            for ext in self.supported_image_formats:
                test_path = self.icons_dir / f"{name}{ext}"
                if test_path.exists():
                    icon_path = test_path
                    break
        
        if icon_path.exists():
            if cache and str(icon_path) in self.asset_cache:
                pixmap = self.asset_cache[str(icon_path)]
            else:
                pixmap = QPixmap(str(icon_path))
                if cache:
                    self.asset_cache[str(icon_path)] = pixmap
            
            return QIcon(pixmap)
        
        return None
    
    def get_pixmap(self, category: str, name: str, cache: bool = True) -> Optional[QPixmap]:
        """Get a pixmap from the specified category."""
        category_dir = self.assets_root / category
        
        if not category_dir.exists():
            return None
        
        # Try different extensions
        pixmap_path = None
        for ext in self.supported_image_formats:
            test_path = category_dir / f"{name}{ext}"
            if test_path.exists():
                pixmap_path = test_path
                break
        
        if pixmap_path:
            if cache and str(pixmap_path) in self.asset_cache:
                return self.asset_cache[str(pixmap_path)]
            else:
                pixmap = QPixmap(str(pixmap_path))
                if cache:
                    self.asset_cache[str(pixmap_path)] = pixmap
                return pixmap
        
        return None
    
    def get_asset_path(self, category: str, name: str) -> Optional[Path]:
        """Get the full path to an asset."""
        category_dir = self.assets_root / category
        
        if not category_dir.exists():
            return None
        
        # Try different extensions based on category
        if category == "sounds":
            extensions = self.supported_sound_formats
        elif category in ["icons", "backgrounds"]:
            extensions = self.supported_image_formats
        elif category == "animations":
            extensions = self.supported_animation_formats
        else:
            extensions = self.supported_image_formats  # Default
        
        for ext in extensions:
            test_path = category_dir / f"{name}{ext}"
            if test_path.exists():
                return test_path
        
        return None
    
    def list_assets(self, category: str) -> List[str]:
        """List all assets in a category."""
        category_dir = self.assets_root / category
        
        if not category_dir.exists():
            return []
        
        assets = []
        
        # Get supported extensions for this category
        if category == "sounds":
            extensions = self.supported_sound_formats
        elif category in ["icons", "backgrounds"]:
            extensions = self.supported_image_formats
        elif category == "animations":
            extensions = self.supported_animation_formats
        else:
            extensions = self.supported_image_formats
        
        for file_path in category_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in extensions:
                assets.append(file_path.stem)
        
        return sorted(assets)
    
    def add_asset(self, category: str, asset_path: Path, name: Optional[str] = None) -> bool:
        """Add a new asset to the specified category."""
        try:
            category_dir = self.assets_root / category
            category_dir.mkdir(exist_ok=True)
            
            # Determine name
            if name is None:
                name = asset_path.stem
            
            # Copy file
            destination = category_dir / f"{name}{asset_path.suffix}"
            shutil.copy2(asset_path, destination)
            
            # Clear cache for this asset if it exists
            cache_key = str(destination)
            if cache_key in self.asset_cache:
                del self.asset_cache[cache_key]
            
            self.asset_added.emit(category, name)
            self.logger.info(f"Added asset '{name}' to category '{category}'")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add asset: {e}")
            return False
    
    def remove_asset(self, category: str, name: str) -> bool:
        """Remove an asset from the specified category."""
        try:
            asset_path = self.get_asset_path(category, name)
            
            if asset_path and asset_path.exists():
                # Remove from cache
                cache_key = str(asset_path)
                if cache_key in self.asset_cache:
                    del self.asset_cache[cache_key]
                
                # Delete file
                asset_path.unlink()
                
                self.asset_removed.emit(category, name)
                self.logger.info(f"Removed asset '{name}' from category '{category}'")
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to remove asset: {e}")
            return False
    
    def rename_asset(self, category: str, old_name: str, new_name: str) -> bool:
        """Rename an asset in the specified category."""
        try:
            old_path = self.get_asset_path(category, old_name)
            
            if not old_path or not old_path.exists():
                return False
            
            # Create new path
            new_path = old_path.parent / f"{new_name}{old_path.suffix}"
            
            # Rename file
            old_path.rename(new_path)
            
            # Update cache
            old_cache_key = str(old_path)
            new_cache_key = str(new_path)
            
            if old_cache_key in self.asset_cache:
                self.asset_cache[new_cache_key] = self.asset_cache.pop(old_cache_key)
            
            self.asset_removed.emit(category, old_name)
            self.asset_added.emit(category, new_name)
            self.logger.info(f"Renamed asset '{old_name}' to '{new_name}' in category '{category}'")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to rename asset: {e}")
            return False
    
    def get_default_icon(self, size: int = 48) -> QIcon:
        """Get a default icon when no specific icon is available."""
        # Create a simple default icon
        pixmap = QPixmap(size, size)
        pixmap.fill()  # Fill with transparent
        
        return QIcon(pixmap)
    
    def clear_cache(self):
        """Clear the asset cache."""
        self.asset_cache.clear()
        self.logger.info("Asset cache cleared")
    
    def get_cache_info(self) -> Dict[str, int]:
        """Get information about the asset cache."""
        return {
            "cached_items": len(self.asset_cache),
            "memory_usage_mb": sum(
                pixmap.width() * pixmap.height() * 4  # 4 bytes per pixel (RGBA)
                for pixmap in self.asset_cache.values()
            ) / (1024 * 1024)
        }
    
    def create_asset_categories(self) -> Dict[str, List[str]]:
        """Get all asset categories and their contents."""
        categories = {}
        
        for category in ["icons", "sounds", "animations", "backgrounds"]:
            categories[category] = self.list_assets(category)
        
        return categories
    
    def export_assets(self, export_path: Path, categories: Optional[List[str]] = None) -> bool:
        """Export assets to a directory."""
        try:
            export_path.mkdir(parents=True, exist_ok=True)
            
            categories_to_export = categories or ["icons", "sounds", "animations", "backgrounds"]
            
            for category in categories_to_export:
                category_dir = self.assets_root / category
                if category_dir.exists():
                    export_category_dir = export_path / category
                    shutil.copytree(category_dir, export_category_dir, dirs_exist_ok=True)
            
            self.logger.info(f"Assets exported to {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export assets: {e}")
            return False
    
    def import_assets(self, import_path: Path, merge: bool = True) -> bool:
        """Import assets from a directory."""
        try:
            if not import_path.exists():
                return False
            
            for category in ["icons", "sounds", "animations", "backgrounds"]:
                import_category_dir = import_path / category
                
                if import_category_dir.exists():
                    target_category_dir = self.assets_root / category
                    
                    if merge:
                        # Merge: copy files, potentially overwriting
                        for file_path in import_category_dir.iterdir():
                            if file_path.is_file():
                                target_path = target_category_dir / file_path.name
                                shutil.copy2(file_path, target_path)
                                
                                # Clear cache for this file
                                cache_key = str(target_path)
                                if cache_key in self.asset_cache:
                                    del self.asset_cache[cache_key]
                    else:
                        # Replace: remove existing and copy new
                        if target_category_dir.exists():
                            shutil.rmtree(target_category_dir)
                        shutil.copytree(import_category_dir, target_category_dir)
            
            # Clear entire cache after import
            self.clear_cache()
            
            self.logger.info(f"Assets imported from {import_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to import assets: {e}")
            return False
