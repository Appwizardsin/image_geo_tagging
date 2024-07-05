import streamlit as st
from PIL import Image
import piexif
from io import BytesIO
import zipfile

def convert_to_rational(number):
    """Converts a number to rational format for EXIF data."""
    f = float(number)
    sign = -1 if f < 0 else 1
    f = abs(f)
    numerator = int(f * 10000)
    denominator = 10000
    return (numerator * sign, denominator)

def add_geotag(image_data, lat, lng):
    try:
        lat = convert_to_rational(lat)
        lng = convert_to_rational(lng)

        zeroth_ifd = {piexif.ImageIFD.Make: u"Make"}
        exif_ifd = {piexif.ExifIFD.UserComment: b"Comment"}
        gps_ifd = {
            piexif.GPSIFD.GPSLatitudeRef: 'N' if lat[0] >= 0 else 'S',
            piexif.GPSIFD.GPSLatitude: ((abs(lat[0]), lat[1]), (0, 1), (0, 1)),
            piexif.GPSIFD.GPSLongitudeRef: 'E' if lng[0] >= 0 else 'W',
            piexif.GPSIFD.GPSLongitude: ((abs(lng[0]), lng[1]), (0, 1), (0, 1)),
        }

        exif_dict = {"0th": zeroth_ifd, "Exif": exif_ifd, "GPS": gps_ifd}
        exif_bytes = piexif.dump(exif_dict)

        im = Image.open(BytesIO(image_data))
        output = BytesIO()
        im.save(output, format="JPEG", exif=exif_bytes)
        return output.getvalue()
    except Exception as e:
        st.error(f"An error occurred while adding geotag: {e}")
        return None

def main():
    st.title("Geotag Image App")
    st.write("Upload images and add coordinates to geotag them.")

    uploaded_files = st.file_uploader("Choose images...", type=["jpg", "jpeg"], accept_multiple_files=True)
    if uploaded_files:
        lat = st.number_input("Enter latitude:", format="%.6f")
        lng = st.number_input("Enter longitude:", format="%.6f")

        if st.button("Geotag Images"):
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
                for uploaded_file in uploaded_files:
                    uploaded_file.seek(0)
                    geotagged_image = add_geotag(uploaded_file.read(), lat, lng)
                    if geotagged_image:
                        zip_file.writestr(uploaded_file.name, geotagged_image)
                        st.image(geotagged_image, caption=f'Geotagged Image: {uploaded_file.name}', use_column_width=True)

            st.download_button(
                label="Download All Geotagged Images",
                data=zip_buffer.getvalue(),
                file_name="geotagged_images.zip",
                mime="application/zip"
            )

if __name__ == "__main__":
    main()
