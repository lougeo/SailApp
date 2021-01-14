import android
import android.activity
from os import remove
from jnius import autoclass, cast

Intent = autoclass('android.content.Intent')
PythonActivity = autoclass('org.kivy.android.PythonActivity')
MediaStore = autoclass('android.provider.MediaStore')
Uri = autoclass('android.net.Uri')


class AndroidCamera:

    def take_picture(self, filename=None, on_complete=None):
        assert(on_complete is not None)
        self.on_complete = on_complete
        self.filename = filename
        android.activity.unbind(on_activity_result=self.on_activity_result)
        android.activity.bind(on_activity_result=self.on_activity_result)
        intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
        uri = Uri.parse('file://' + filename)
        print(f"URI: {uri}")
        parcelable = cast('android.os.Parcelable', uri)
        print(f"PARCELABLE: {parcelable}")
        intent.putExtra(MediaStore.EXTRA_OUTPUT, parcelable)
        PythonActivity.mActivity.startActivityForResult(intent, 0x123)

    def on_activity_result(self, requestCode, resultCode, intent):
        if requestCode != 0x123:
            "REQUEST CODE INCORRECT"
            return
        android.activity.unbind(on_activity_result=self.on_activity_result)
        if self.on_complete(self.filename):
            print("TRIGGERING REMOVE")
            self.remove(self.filename)

    def remove(self, fn):
        try:
            remove(fn)
        except OSError:
            pass