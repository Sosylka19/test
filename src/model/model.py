# from PIL import Image, ImageOps
# import requests
# from io import BytesIO
# import time
# from retinaface import RetinaFace
# import numpy as np

# def rec(url):
#     response = requests.get(url)
#     img = Image.open(BytesIO(response.content))
#     img = ImageOps.exif_transpose(img)
#     img = np.array(img.convert('RGB'))

#     result = RetinaFace.detect_faces(img)
#     return result


# def recognize():
#     with open("data/avatars.txt", "r") as f:
#         emails = f.readlines()
#         #first - url, second - email
#         emails = [email[:-1].split() for email in emails]
#         return emails
  
# b = recognize()
# print(len(b))
# timeit = time.time()
# print(rec(b[0][0]))
# print(time.time() - timeit)

# fast_avatar_pipeline.py
# Python 3.10+, pip install httpx pillow numpy retina-face

import asyncio
from typing import List, Tuple, Optional
import io

import httpx   
import time                    
import numpy as np
from PIL import Image, ImageOps
from retinaface import RetinaFace    

MAX_CONCURRENCY = 24    
HTTP_TIMEOUT = httpx.Timeout(20.0)
ACCEPTED_PREFIX = "image/"

async def fetch_image(client: httpx.AsyncClient, url: str) -> Optional[bytes]:
    r = await client.get(url, follow_redirects=True)
    if r.status_code != 200:
        return None
    ctype = r.headers.get("Content-Type", "")
    if not ctype.startswith(ACCEPTED_PREFIX):
        return None
    return r.content

def pill_to_img(img: Image.Image) -> np.ndarray:
    img = ImageOps.exif_transpose(img)
    return np.array(img.convert('RGB'))

async def donwload(urls: List[str]) -> List[Tuple[str, Optional[bytes]]]:
    async with httpx.AsyncClient(http2=True, timeout=HTTP_TIMEOUT) as client:
        sem = asyncio.Semaphore(MAX_CONCURRENCY)

        async def task(u: str):
            async with sem:
                try:
                    img = await fetch_image(client, u)
                    return (u, img)
                except httpx.HTTPError:
                    return (u, None)
                
        return await asyncio.gather(*[task(u) for u in urls])
    

def detect_faces(img_bytes: List[Tuple[str, Optional[bytes]]]) -> List[Tuple[str, bool, dict]]:
    results = []
    for url, b in img_bytes:
        if b is None:
            results.append((url, False, {"reason": "no image bytes", "face_area_percent": 0}))
            continue
        try:
            with Image.open(io.BytesIO(b)) as pil_img:
                arr = pill_to_img(pil_img)
        except Exception as e:
            results.append((url, False, {"reason": f"cannot open image: {e}", "face_area_percent": 0}))
            continue

        try:
            out = RetinaFace.detect_faces(arr)
            length = (out['face_1']['facial_area'][3] - out['face_1']['facial_area'][1])
            width = (out['face_1']['facial_area'][2] - out['face_1']['facial_area'][0])
            
            img_area = np.shape(arr)[:-1]
            face_area_percent = (length * width) / (img_area[0] * img_area[1]) * 100
            if isinstance(out, dict) and len(out) > 0:
                results.append((url, True, {"faces": len(out), "face_area_percent": face_area_percent}))
            else:
                results.append((url, False, {"reason": 0, "face_area_percent": 0}))
        except Exception as e:
            results.append((url, False, {"reason": f"retinaface error: {e}", "face_area_percent": 0}))
    return results

# async def main():
#     with open("data/avatars.txt", "r") as f:
#         emails = f.readlines()
#         #first - url, second - email
#         emails = [email[:-1].split() for email in emails]
#         urls = [email[0] for email in emails]

#     start_time = time.time()
#     img_bytes = await donwload(urls)
#     download_time = time.time()
#     print(f"Downloaded {len(img_bytes)} images in {download_time - start_time:.2f} seconds")

#     results = detect_faces(img_bytes)
#     detect_time = time.time()
#     print(f"Processed {len(results)} images in {detect_time - download_time:.2f} seconds")

#     with open("data/avatars_detection.csv", "w", encoding='utf-8') as f:
#         f.write("url,has_face,info\n")

#         for url, has_face, info in results:
#             f.write(f"{url},{has_face},{info}\n")

#     total = len(results)
#     has_face = sum(1 for _, hf, _ in results if hf)
#     print(f"Total: {total}, with faces: {has_face}, without faces: {total - has_face}")


def threshold(face_area_percent, threshold=8) -> bool:
    if face_area_percent > threshold:
        return True
    return False
    

async def main():
    with open("data/avatars.txt", "r") as f:
        emails = f.readlines()
        #first - url, second - email
        emails = [email[:-1].split() for email in emails]
        urls = [email[0] for email in emails]
        email = [email[1] for email in emails]

    img_bytes = await donwload(urls[:2])

    results = detect_faces(img_bytes)
    results_email = list(zip(results, email[:2]))
    with open("data/faces_summary.csv",  "a+") as f:
        f.write("url, email, face_area_percentage\n")
    for user, email in results_email:

        url, has_face, info = user
        if not (has_face and threshold(info.get("face_area_percent", 0))):
            with open("data/faces_summary.csv", "a+") as f:
                f.write(f"{url}, {email}, {info.get('face_area_percentage', 0)}\n")
            


if __name__ == "__main__":
    asyncio.run(main())

        