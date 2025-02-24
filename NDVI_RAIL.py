# import streamlit as st
# import geopandas as gpd
# import ee
# import json
# import os
# import tempfile
# import geemap.foliumap as geemap
# from io import BytesIO
# from datetime import datetime
# from io import StringIO
# from PIL import Image
# from google.oauth2 import service_account
#
# import streamlit as st
# from PIL import Image
#
# # بارگذاری تصویر
# image = Image.open("ABK.jpg")  # مسیر تصویر محلی خود را وارد کنید
#
# # streamlisاستفاده از Sidebar برای نمایش تصویر در بالای آن
# with st.sidebar:
#     st.image(image, use_container_width=True)
#     st.markdown('<h2 style="color: green;">شرکت مهندسین مشاور آسمان برج کارون</h2>', unsafe_allow_html=True)
#
# # مقداردهی اولیه GEE
#
# # # مقداردهی اولیه GEE
# # service_account = "iman.e.bakhshipoor@gmail.com"
# # credentials = ee.ServiceAccountCredentials(service_account, "IMAN_GEE.json")
# # ee.Initialize(credentials)
#
#
# # from google.oauth2 import service_account
# #
# # # دریافت کلید سرویس از متغیر محیطی
# # service_account_info = json.loads(os.getenv("GEE_SERVICE_ACCOUNT"))
# # credentials = service_account.Credentials.from_service_account_info(service_account_info)
# #
# # # مقداردهی اولیه Google Earth Engine
# # ee.Initialize(credentials)
#
# from google.auth import exceptions
# from google.oauth2 import service_account
#
# # دریافت اطلاعات کلید سرویس از متغیر محیطی
# key_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
# credentials_info = json.loads(key_json)
#
# # استفاده از اعتبارنامه‌ها
# credentials = service_account.Credentials.from_service_account_info(credentials_info, scopes=["https://www.googleapis.com/auth/earthengine", "https://www.googleapis.com/auth/cloud-platform"])
#
# try:
#     ee.Initialize(credentials)
# except exceptions.RefreshError as e:
#     print(f"Error initializing: {e}")
#
# # آپلود فایل ZIP شامل Shapefile
# uploaded_file = st.file_uploader("آپلود یک شیپ فایل فشرده ‌شده (.zip)", type=["zip"])
#
# # استفاده از Sidebar برای انتخاب تاریخ و مقیاس
# with st.sidebar:
#     start_date = st.date_input("تاریخ شروع", value=datetime(2025, 1, 1), min_value=datetime(2000, 1, 1),
#                                max_value=datetime.today())
#     end_date = st.date_input("تاریخ پایان", value=datetime(2025, 2, 15), min_value=datetime(2000, 1, 1),
#                              max_value=datetime.today())
#     scale = st.number_input("مقیاس (Scale)", min_value=10, max_value=100, value=10, step=10)
#
# if uploaded_file:
#     try:
#         gdf = gpd.read_file(BytesIO(uploaded_file.getvalue()))
#         if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
#             gdf = gdf.to_crs(epsg=4326)
#         st.write("CRS Shapefile (converted):", gdf.crs)
#         st.write(" Shapefile:", gdf.geometry)
#
#         geojson = json.loads(gdf.to_json())
#         features = [ee.Feature(feature) for feature in geojson["features"]]
#         region = ee.FeatureCollection(features)
#
#         start_date_ee = ee.Date.fromYMD(start_date.year, start_date.month, start_date.day)
#         end_date_ee = ee.Date.fromYMD(end_date.year, end_date.month, end_date.day)
#
#         image = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
#             .filterBounds(region) \
#             .filterDate(start_date_ee, end_date_ee).median() \
#             .clip(region)
#
#         if image is None:
#             st.error("هیچ تصویری از Sentinel-2 برای این منطقه و بازه زمانی یافت نشد.")
#         else:
#             ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
#             savi = image.expression(
#                 "((B8 - B4) / (B8 + B4 + 0.5)) * (1.5)",
#                 {
#                     'B8': image.select('B8'),
#                     'B4': image.select('B4')
#                 }
#             ).rename("SAVI")
#             mndwi = image.normalizedDifference(["B3", "B11"]).rename("MNDWI")
#             gcvi = image.expression("B8 / B3 - 1", {
#                 'B8': image.select('B8'),
#                 'B3': image.select('B3')
#             }).rename("GCVI")
#
#             composite = ndvi.addBands([savi, mndwi, gcvi])
#
#             Map = geemap.Map(center=[gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()], zoom=8)
#             Map.add_basemap("OpenStreetMap")
#             Map.add_basemap("HYBRID")
#             Map.addLayer(ndvi, {'min': 0, 'max': 1, 'palette': ['white', 'green']}, "NDVI", False)
#             Map.addLayer(savi, {'min': 0, 'max': 1, 'palette': ['white', 'yellow', 'green']}, "SAVI", False)
#             Map.addLayer(mndwi, {'min': -1, 'max': 1, 'palette': ['red', 'blue']}, "MNDWI", False)
#             Map.addLayer(gcvi, {'palette': ['#ffffff', '#ffff00', '#008000'], 'min': 0.347, 'max': 3.704}, "GCVI",
#                          False)
#             Map.addLayer(image, {'min': 0, 'max': 3000, 'bands': ["B4", "B3", "B2"]}, "True Color", True)
#             Map.addLayer(region, {}, " Shapefile")
#
#             Map.to_streamlit(height=600)
#
#
#             def download_image(image, filename):
#                 with st.spinner(f"در حال تولید {filename}... ⏳"):
#                     temp_dir = tempfile.gettempdir()
#                     temp_path = os.path.join(temp_dir, filename)
#                     geemap.ee_export_image(image, filename=temp_path, scale=scale, region=region.geometry().bounds())
#                     with open(temp_path, "rb") as f:
#                         st.download_button(label=f"download  {filename}", data=f, file_name=filename, mime="image/tiff")
#
#
#             st.subheader("download image")
#             download_image(ndvi, "ndvi_image.tif")
#             download_image(savi, "savi_image.tif")
#             download_image(mndwi, "mndwi_image.tif")
#             download_image(gcvi, "gcvi_image.tif")
#     except Exception as e:
#         st.error(f"خطا در پردازش Shapefile یا محاسبه شاخص‌ها: {str(e)}")

#####################################################################################
# import streamlit as st
# import geopandas as gpd
# import ee
# import json
# import os
# import tempfile
# import geemap.foliumap as geemap
# from io import BytesIO
# from datetime import datetime
# from PIL import Image
# from google.oauth2 import service_account
#
# # بارگذاری تصویر
# image = Image.open("ABK.jpg")  # مسیر تصویر محلی خود را وارد کنید
#
# # streamlit استفاده از Sidebar برای نمایش تصویر در بالای آن
# with st.sidebar:
#     st.image(image, use_container_width=True)
#     st.markdown('<h2 style="color: green;">شرکت مهندسین مشاور آسمان برج کارون</h2>', unsafe_allow_html=True)
#
#
#
#
#
#
#
#
#
# from google.auth import exceptions
# from google.oauth2 import service_account
#
# # دریافت اطلاعات کلید سرویس از متغیر محیطی
# key_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
# credentials_info = json.loads(key_json)
#
# # استفاده از اعتبارنامه‌ها
# credentials = service_account.Credentials.from_service_account_info(credentials_info, scopes=["https://www.googleapis.com/auth/earthengine", "https://www.googleapis.com/auth/cloud-platform"])
#
# try:
#     ee.Initialize(credentials)
# except exceptions.RefreshError as e:
#     print(f"Error initializing: {e}")
#
#
#
#
#
#
#
#
#
#
#
# # آپلود فایل ZIP شامل Shapefile
# uploaded_file = st.file_uploader("آپلود یک شیپ فایل فشرده ‌شده (.zip)", type=["zip"])
#
# # استفاده از Sidebar برای انتخاب تاریخ و مقیاس
# with st.sidebar:
#     start_date = st.date_input("تاریخ شروع", value=datetime(2025, 1, 1), min_value=datetime(2000, 1, 1),
#                                max_value=datetime.today())
#     end_date = st.date_input("تاریخ پایان", value=datetime(2025, 2, 15), min_value=datetime(2000, 1, 1),
#                              max_value=datetime.today())
#     scale = st.number_input("مقیاس (Scale)", min_value=10, max_value=100, value=10, step=10)
#
# # تابع دانلود تصویر (باید قبل از صدا زدن تعریف شود)
# def download_image(image, filename, region, scale):
#     with st.spinner(f"در حال تولید {filename}... ⏳"):
#         temp_dir = tempfile.gettempdir()
#         temp_path = os.path.join(temp_dir, filename)
#         geemap.ee_export_image(image, filename=temp_path, scale=scale, region=region.geometry().bounds())
#         with open(temp_path, "rb") as f:
#             st.download_button(label=f"Download {filename}", data=f, file_name=filename, mime="image/tiff")
#
# if uploaded_file:
#     try:
#         gdf = gpd.read_file(BytesIO(uploaded_file.getvalue()))
#         if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
#             gdf = gdf.to_crs(epsg=4326)
#         st.write("CRS Shapefile (converted):", gdf.crs)
#         st.write("Shapefile:", gdf.geometry)
#
#         geojson = json.loads(gdf.to_json())
#         features = [ee.Feature(feature) for feature in geojson["features"]]
#         region = ee.FeatureCollection(features)
#
#         start_date_ee = ee.Date.fromYMD(start_date.year, start_date.month, start_date.day)
#         end_date_ee = ee.Date.fromYMD(end_date.year, end_date.month, end_date.day)
#
#         image = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
#             .filterBounds(region) \
#             .filterDate(start_date_ee, end_date_ee).median() \
#             .clip(region)
#
#         if image is None:
#             st.error("هیچ تصویری از Sentinel-2 برای این منطقه و بازه زمانی یافت نشد.")
#         else:
#             ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
#             mndwi = image.normalizedDifference(["B3", "B11"]).rename("MNDWI")
#
#             composite = ndvi.addBands([mndwi])
#
#             Map = geemap.Map(center=[gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()], zoom=8)
#             Map.add_basemap("OpenStreetMap")
#             Map.add_basemap("HYBRID")
#             Map.addLayer(ndvi, {'min': 0, 'max': 1, 'palette': ['white', 'green']}, "Crop Detection", False)
#             Map.addLayer(mndwi, {'min': -1, 'max': 1, 'palette': ['red', 'blue']}, "Water Body", False)
#             Map.addLayer(image, {'min': 0, 'max': 3000, 'bands': ["B4", "B3", "B2"]}, "True Color", True)
#             Map.addLayer(region, {}, "Shapefile")
#
#             Map.to_streamlit(height=600)
#
#             # اضافه کردن دکمه برای نمایش radiobutton
#             if st.button("Download Image"):
#                 download_choice = st.radio(
#                     "کدام تصویر را می خواهید دانلود کنید؟",
#                     ("Crop Detection", "Water Body")  # حذف گزینه True Color از این لیست
#                 )
#
#                 # بخش دانلود تصاویر
#                 st.subheader("Download Image")
#                 if download_choice == "NDVI":
#                     download_image(ndvi, "Crop-Detection.tif", region, scale)
#                 elif download_choice == "MNDWI":
#                     download_image(mndwi, "Water-Body.tif", region, scale)
#     except Exception as e:
#         st.error(f"خطا در پردازش Shapefile یا محاسبه شاخص‌ها: {str(e)}")
#
#




#
# import streamlit as st
# import geopandas as gpd
# import ee
# import json
# import os
# import tempfile
# import geemap.foliumap as geemap
# from io import BytesIO
# from datetime import datetime
# from PIL import Image
# from google.oauth2 import service_account
#
# # بارگذاری تصویر
# image = Image.open("ABK.jpg")  # مسیر تصویر محلی خود را وارد کنید
#
# # streamlit استفاده از Sidebar برای نمایش تصویر در بالای آن
# with st.sidebar:
#     st.image(image, use_container_width=True)
#     st.markdown('<h2 style="color: green;">شرکت مهندسین مشاور آسمان برج کارون</h2>', unsafe_allow_html=True)
#
#
#
# from google.auth import exceptions
# from google.oauth2 import service_account
#
# # دریافت اطلاعات کلید سرویس از متغیر محیطی
# key_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
# credentials_info = json.loads(key_json)
#
# # استفاده از اعتبارنامه‌ها
# credentials = service_account.Credentials.from_service_account_info(credentials_info, scopes=["https://www.googleapis.com/auth/earthengine", "https://www.googleapis.com/auth/cloud-platform"])
#
# try:
#     ee.Initialize(credentials)
# except exceptions.RefreshError as e:
#     print(f"Error initializing: {e}")
#
#
#
#
#
#
# # آپلود فایل ZIP شامل Shapefile
# uploaded_file = st.file_uploader("آپلود یک شیپ فایل فشرده ‌شده (.zip)", type=["zip"])
#
# # استفاده از Sidebar برای انتخاب تاریخ و مقیاس
# with st.sidebar:
#     start_date = st.date_input("تاریخ شروع", value=datetime(2025, 1, 1), min_value=datetime(2000, 1, 1),
#                                max_value=datetime.today())
#     end_date = st.date_input("تاریخ پایان", value=datetime(2025, 2, 15), min_value=datetime(2000, 1, 1),
#                              max_value=datetime.today())
#     scale = st.number_input("مقیاس (Scale)", min_value=10, max_value=100, value=10, step=10)
#
# # تابع دانلود تصویر (باید قبل از صدا زدن تعریف شود)
# def download_image(image, filename, region, scale):
#     with st.spinner(f"در حال تولید {filename}... ⏳"):
#         temp_dir = tempfile.gettempdir()
#         temp_path = os.path.join(temp_dir, filename)
#         geemap.ee_export_image(image, filename=temp_path, scale=scale, region=region.geometry().bounds())
#         with open(temp_path, "rb") as f:
#             st.download_button(label=f"Download {filename}", data=f, file_name=filename, mime="image/tiff")
#
# if uploaded_file:
#     try:
#         gdf = gpd.read_file(BytesIO(uploaded_file.getvalue()))
#         if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
#             gdf = gdf.to_crs(epsg=4326)
#         st.write("CRS Shapefile (converted):", gdf.crs)
#         st.write("Shapefile:", gdf.geometry)
#
#         geojson = json.loads(gdf.to_json())
#         features = [ee.Feature(feature) for feature in geojson["features"]]
#         region = ee.FeatureCollection(features)
#
#         start_date_ee = ee.Date.fromYMD(start_date.year, start_date.month, start_date.day)
#         end_date_ee = ee.Date.fromYMD(end_date.year, end_date.month, end_date.day)
#
#         image = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
#             .filterBounds(region) \
#             .filterDate(start_date_ee, end_date_ee).median() \
#             .clip(region)
#
#         if image is None:
#             st.error("هیچ تصویری از Sentinel-2 برای این منطقه و بازه زمانی یافت نشد.")
#         else:
#             ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
#             mndwi = image.normalizedDifference(["B3", "B11"]).rename("MNDWI")
#
#             composite = ndvi.addBands([mndwi])
#
#             Map = geemap.Map(center=[gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()], zoom=8)
#             Map.add_basemap("OpenStreetMap")
#             Map.add_basemap("HYBRID")
#             Map.addLayer(ndvi, {'min': 0, 'max': 1, 'palette': ['white', 'green']}, "Crop Detection", False)
#             Map.addLayer(mndwi, {'min': -1, 'max': 1, 'palette': ['red', 'blue']}, "Water Body", False)
#             Map.addLayer(image, {'min': 0, 'max': 3000, 'bands': ["B4", "B3", "B2"]}, "True Color", True)
#             Map.addLayer(region, {}, "Shapefile")
#
#             Map.to_streamlit(height=600)
#
#             # اضافه کردن دکمه برای نمایش radiobutton
#             if st.button("Download Image"):
#                 download_choice = st.radio(
#                     "کدام تصویر را می خواهید دانلود کنید؟",
#                     ("Crop Detection", "Water Body")  # حذف گزینه True Color از این لیست
#                 )
#
#                 # بخش دانلود تصاویر
#                 st.subheader("Download Image")
#                 if download_choice == "NDVI":
#                     download_image(ndvi, "Crop-Detection.tif", region, scale)
#                 elif download_choice == "MNDWI":
#                     download_image(mndwi, "Water-Body.tif", region, scale)
#     except Exception as e:
#         st.error(f"خطا در پردازش Shapefile یا محاسبه شاخص‌ها: {str(e)}")


import streamlit as st
import geopandas as gpd
import ee
import json
import os
import tempfile
import geemap.foliumap as geemap
from io import BytesIO
from datetime import datetime
from PIL import Image
from google.oauth2 import service_account

# بارگذاری تصویر
image = Image.open("ABK.jpg")

# نمایش تصویر در نوار کناری
with st.sidebar:
    st.image(image, use_container_width=True)
    st.markdown('<h2 style="color: green;">شرکت مهندسین مشاور آسمان برج کارون</h2>', unsafe_allow_html=True)

# احراز هویت Google Earth Engine
key_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
credentials_info = json.loads(key_json)
credentials = service_account.Credentials.from_service_account_info(credentials_info, scopes=[
    "https://www.googleapis.com/auth/earthengine", "https://www.googleapis.com/auth/cloud-platform"])
try:
    ee.Initialize(credentials)
except Exception as e:
    st.error(f"خطا در احراز هویت: {e}")

# آپلود فایل ZIP شامل Shapefile
uploaded_file = st.file_uploader("آپلود یک شیپ فایل فشرده ‌شده (.zip)", type=["zip"])

# انتخاب تاریخ و مقیاس
with st.sidebar:
    start_date = st.date_input("تاریخ شروع", value=datetime(2025, 1, 1))
    end_date = st.date_input("تاریخ پایان", value=datetime(2025, 2, 15))
    scale = st.number_input("مقیاس (Scale)", min_value=10, max_value=100, value=10, step=10)

# پردازش و نمایش تصاویر
if uploaded_file:
    try:
        gdf = gpd.read_file(BytesIO(uploaded_file.getvalue()))
        if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs(epsg=4326)

        st.write("Shapefile CRS:", gdf.crs)
        region = ee.FeatureCollection([ee.Feature(json.loads(gdf.to_json())["features"][0])])

        start_date_ee = ee.Date.fromYMD(start_date.year, start_date.month, start_date.day)
        end_date_ee = ee.Date.fromYMD(end_date.year, end_date.month, end_date.day)

        image = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED").filterBounds(region).filterDate(start_date_ee,
                                                                                                  end_date_ee).median().clip(
            region)

        if image is None:
            st.error("هیچ تصویری یافت نشد.")
        else:
            ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
            mndwi = image.normalizedDifference(["B3", "B11"]).rename("MNDWI")

            # ذخیره تصاویر در session_state برای جلوگیری از پردازش مجدد
            st.session_state["ndvi"] = ndvi
            st.session_state["mndwi"] = mndwi
            st.session_state["region"] = region

            Map = geemap.Map(center=[gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()], zoom=8)
            Map.add_basemap("OpenStreetMap")
            Map.addLayer(ndvi, {'min': 0, 'max': 1, 'palette': ['white', 'green']}, "Crop Detection")
            Map.addLayer(mndwi, {'min': -1, 'max': 1, 'palette': ['red', 'blue']}, "Water Body")
            Map.addLayer(image, {'min': 0, 'max': 3000, 'bands': ["B4", "B3", "B2"]}, "True Color")
            Map.addLayer(region, {}, "Shapefile")
            Map.to_streamlit(height=600)
    except Exception as e:
        st.error(f"خطا در پردازش Shapefile: {e}")


# تابع دانلود تصویر
def download_image(image, filename, region, scale):
    with st.spinner(f"در حال تولید {filename}..."):
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, filename)
        geemap.ee_export_image(image, filename=temp_path, scale=scale, region=region.geometry().bounds())
        with open(temp_path, "rb") as f:
            st.download_button(label=f"Download {filename}", data=f, file_name=filename, mime="image/tiff")


# دکمه دانلود تصاویر بعد از نمایش
if "ndvi" in st.session_state and "mndwi" in st.session_state and "region" in st.session_state:
    if st.button("Download All Images"):
        download_image(st.session_state["ndvi"], "Crop-Detection.tif", st.session_state["region"], scale)
        download_image(st.session_state["mndwi"], "Water-Body.tif", st.session_state["region"], scale)
