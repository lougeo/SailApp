import android
import android.activity
from jnius import autoclass, cast
from kivy.clock import mainthread
from os import remove
import time

Intent = autoclass("android.content.Intent")
PythonActivity = autoclass("org.kivy.android.PythonActivity")
MediaStore = autoclass("android.provider.MediaStore")
Uri = autoclass("android.net.Uri")
FileProvider = autoclass("android.support.v4.content.FileProvider")
Context = autoclass("android.content.Context")
Environment = autoclass("android.os.Environment")
File = autoclass("java.io.File")


class AndroidCamera:

    CAMERA_REQUEST_CODE = 1450

    def __init__(self):
        self.currentActivity = cast("android.app.Activity", PythonActivity.mActivity)

    def take_picture(self, on_complete):

        self.on_complete = on_complete

        camera_intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)

        photo_file = self._create_image_file()

        if photo_file is not None:
            photo_uri = FileProvider.getUriForFile(
                Context.getApplicationContext(),
                "com.sailmeter.sailapp",
                # self.currentActivity.getApplicationContext().getPackageName() + '.provider',
                photo_file,
            )

            parcelable = cast("android.os.Parcelable", photo_uri)

            android.activity.unbind(on_activity_result=self.on_activity_result)
            android.activity.bind(on_activity_result=self.on_activity_result)

            camera_intent.putExtra(MediaStore.EXTRA_OUTPUT, parcelable)
            self.currentActivity.startActivityForResult(
                camera_intent, self.CAMERA_REQUEST_CODE
            )

    @mainthread
    def on_activity_result(self, request_code, request_code2, intent):
        if request_code == self.CAMERA_REQUEST_CODE:
            android.activity.unbind(on_activity_result=self.on_activity_result)
            self.on_complete(self.image_path)

    def _create_image_file(self):
        timestamp = time.strftime("%Y%m%d_%H%M%S", time.gmtime())
        image_file_name = "IMG_" + timestamp + "_"
        storage_dir = Context.getExternalFilesDir(Environment.DIRECTORY_PICTURES)
        image = File.createTempFile(image_file_name, ".jpg", storage_dir)
        self.image_path = image.getAbsolutePath()
        return image