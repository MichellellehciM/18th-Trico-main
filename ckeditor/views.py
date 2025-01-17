from django.http import JsonResponse
from django.conf import settings
from django.core.files.storage import default_storage
from PIL import Image
import os
from django.views.decorators.csrf import csrf_exempt





def process_file_for_browse(original_file_path, processed_file_path):
    """
    處理檔案（如生成縮圖），並存儲到指定路徑
    """
    with Image.open(original_file_path) as img:
        # 生成縮圖
        img.thumbnail((300, 300))  # 縮圖大小設定
        img.save(processed_file_path)


@csrf_exempt
def file_upload_view(request):

    if request.method == "POST" and request.FILES.get("upload"):
        file = request.FILES["upload"]

        # 存儲到 upload 資料夾
        original_path = os.path.join(settings.MEDIA_ROOT, "uploads", file.name)
        default_storage.save(original_path, file)

        # 處理檔案，存儲到 browse 資料夾
        processed_path = os.path.join(settings.MEDIA_ROOT, "browse", file.name)
        process_file_for_browse(original_path, processed_path)

        # 返回處理後的檔案 URL
        file_url = default_storage.url(f"browse/{file.name}")

        return JsonResponse(
            {
                "url": file_url,
                "uploaded": True,
            }
        )

    return JsonResponse(
        {"uploaded": False, "error": {"message": "Invalid upload request"}}
    )


def file_browse_view(request):
    """
    列出 browse 資料夾中的檔案
    """
    folder = os.path.join(settings.MEDIA_ROOT, "browse")
    files = []

    if default_storage.exists(folder):
        for file_name in default_storage.listdir(folder)[1]:
            file_url = default_storage.url(f"browse/{file_name}")
            files.append(
                {
                    "url": file_url,
                    "name": file_name,
                }
            )

    return JsonResponse({"files": files})


def process_file_to_browse_s3(original_file_path, output_path):
    try:
        """
        從 upload 處理檔案並上傳到 browse 資料夾
        """
        with default_storage.open(original_file_path, "rb") as original_file:
            with Image.open(original_file) as img:
                # 縮圖大小
                img.thumbnail((300, 300))
                # 將處理後的圖片存到 browse 資料夾
                with default_storage.open(output_path, "wb") as output_file:
                    img.save(output_file, format=img.format)
    except Exception as e:
        print(f"Error during image processing: {e}")
        raise


@csrf_exempt
def file_upload_view(request):
    if request.method == "POST" and request.FILES.get("upload"):
        file = request.FILES["upload"]

        # 上傳到 upload 資料夾
        upload_path = f"upload/{file.name}"
        default_storage.save(upload_path, file)

        # 處理檔案，存到 browse 資料夾
        browse_path = f"browse/{file.name}"
        process_file_to_browse_s3(upload_path, browse_path)

        # 返回處理後的檔案 URL
        file_url = default_storage.url(browse_path)
        print(f"Generated file URL: {file_url}")  # 打印 URL


        return JsonResponse(
            {
                "url": file_url,
                "uploaded": True,
            }
        )

    return JsonResponse(
        {"uploaded": False, "error": {"message": "Invalid upload request"}}
    )


def file_browse_view(request):
    """
    列出 S3 browse 資料夾中的檔案
    """
    browse_folder = "browse/"
    files = []

    # 使用 S3 列出 browse 資料夾內的所有檔案
    for file_name in default_storage.listdir(browse_folder)[1]:
        file_url = default_storage.url(f"{browse_folder}{file_name}")
        files.append(
            {
                "url": file_url,
                "name": file_name,
            }
        )

    return JsonResponse({"files": files})



