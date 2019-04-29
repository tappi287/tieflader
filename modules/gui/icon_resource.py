from PySide2.QtGui import QIcon, QPixmap, QFontDatabase, QFont
from modules.app_globals import Resource
from modules.log import init_logging

LOGGER = init_logging(__name__)


class IconRsc:
    # Store loaded icons here
    icon_storage = {
        'example_key': QIcon()
        }

    @classmethod
    def get_pixmap(cls, icon_key: str):
        if icon_key not in Resource.icon_paths.keys():
            return QPixmap()

        return QPixmap(Resource.icon_paths[icon_key])

    @classmethod
    def get_icon(cls, icon_key: str) -> QIcon:
        if icon_key not in cls.icon_storage.keys():

            if icon_key in Resource.icon_paths.keys():
                icon = QIcon(QPixmap(Resource.icon_paths[icon_key]))
            else:
                icon = QIcon()

            cls.icon_storage[icon_key] = icon

        return cls.icon_storage[icon_key]


class FontRsc:
    font_storage = {
        'example_key': None
        }

    regular = None
    italic = None

    small_pixel_size = 16
    regular_pixel_size = 18
    big_pixel_size = 20

    default_font_key = 'OpenSans-Regular'

    @classmethod
    def init(cls, size: int=0):
        """
            Needs to be initialized after QApplication is running
            QFontDatabase is not available prior to app start
        """
        if not size:
            size = cls.regular_pixel_size

        cls.regular = QFont(cls.default_font_key)
        cls.regular.setPixelSize(size)
        cls.italic = QFont(cls.default_font_key)
        cls.italic.setPixelSize(size)
        cls.italic.setItalic(True)

    @classmethod
    def add_to_font_db(cls, font_key):
        font_id = QFontDatabase.addApplicationFont(Resource.icon_paths[font_key])
        cls.font_storage[font_key] = font_id
        LOGGER.debug('Font loaded and added to db: %s', QFontDatabase.applicationFontFamilies(font_id))

        return QFont(QFontDatabase.applicationFontFamilies(font_id)[0], 8)

    @classmethod
    def get_font(cls, font_key) -> QFont():
        if font_key in cls.font_storage.keys():
            return QFont(QFontDatabase.applicationFontFamilies(cls.font_storage[font_key])[0], 8)

        if font_key in Resource.icon_paths.keys():
            return cls.add_to_font_db(font_key)

        return QFont()
