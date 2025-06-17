customColorPalette = [
        {
            "color": "hsl(4, 90%, 58%)",
            "label": "Red"
        },
        {
            "color": "hsl(340, 82%, 52%)",
            "label": "Pink"
        },
        {
            "color": "hsl(291, 64%, 42%)",
            "label": "Purple"
        },
        {
            "color": "hsl(262, 52%, 47%)",
            "label": "Deep Purple"
        },
        {
            "color": "hsl(231, 48%, 48%)",
            "label": "Indigo"
        },
        {
            "color": "hsl(207, 90%, 54%)",
            "label": "Blue"
        },
    ]

# CKEditor 配置
# SESSION_COOKIE_HTTPONLY = True
# CSRF_COOKIE_HTTPONLY = True
# X_FRAME_OPTIONS = "DENY"






CKEDITOR_UPLOAD_PATH = "uploads/"  # 圖片上傳後存儲的目錄
CKEDITOR_BROWSE_PATH = "browse/"   # 瀏覽專用文件夾
CKEDITOR_5_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
CKEDITOR_5_ALLOW_ALL_FILE_TYPES = True
CKEDITOR_5_UPLOAD_FILE_TYPES = ["jpeg", "jpg", "png", "gif", "webp", "tiff", "bmp", "svg"] 

CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "heading", "|", "bold", "italic", "link", "bulletedList", 
            "numberedList", "blockQuote", "imageUpload"
        ],
        "filebrowserUploadUrl": "/ckeditor5/upload/",
        "filebrowserBrowseUrl": "/ckeditor5/browse/",
    },
    "extends": {
        "blockToolbar": [
            "paragraph", "heading1", "heading2", "heading3", "|",
            "bulletedList", "numberedList", "|", "blockQuote"
        ],
        "toolbar": [
            "heading", "|", "outdent", "indent", "|", "bold", "italic", 
            "link", "underline", "strikethrough", "code", "subscript", 
            "superscript", "highlight", "|", "codeBlock", "sourceEditing", 
            "imageUpload", "bulletedList", "numberedList", "todoList", "|", 
            "blockQuote", "fontSize", "fontFamily", "fontColor", 
            "fontBackgroundColor", "mediaEmbed", "removeFormat", "insertTable"
        ],
        "image": {
            "toolbar": [
                "imageTextAlternative", "|", "imageStyle:alignLeft", 
                "imageStyle:alignRight", "imageStyle:alignCenter", 
                "imageStyle:side", "|"
            ],
            "styles": [
                "full", "side", "alignLeft", "alignRight", "alignCenter"
            ]
        },
        "table": {
            "contentToolbar": [
                "tableColumn", "tableRow", "mergeTableCells", 
                "tableProperties", "tableCellProperties"
            ],
            "tableProperties": {
                "borderColors": customColorPalette,
                "backgroundColors": customColorPalette
            },
            "tableCellProperties": {
                "borderColors": customColorPalette,
                "backgroundColors": customColorPalette
            }
        }
    }
}


# Define a constant in settings.py to specify file upload permissions
CKEDITOR_5_FILE_UPLOAD_PERMISSION = "authenticated"  # Possible values: "staff", "authenticated", "any"