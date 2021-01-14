import android
import android.activity
from os import remove
from jnius import autoclass, cast

Intent = autoclass('android.content.Intent')
PythonActivity = autoclass('org.kivy.android.PythonActivity')
MediaStore = autoclass('android.provider.MediaStore')
Uri = autoclass('android.net.Uri')
FileProvider = autoclass('android.support.v4.content.FileProvider')


class AndroidCamera:

    def take_picture(self, filename=None, on_complete=None):
        assert(on_complete is not None)
        self.on_complete = on_complete
        self.filename = filename
        android.activity.unbind(on_activity_result=self._on_activity_result)
        android.activity.bind(on_activity_result=self._on_activity_result)
        intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
        # uri = Uri.parse('file:/' + filename)
        # print(f"URI: {uri}")
        fileprovider = FileProvider('content:/' + filename)
        parcelable = cast('android.os.Parcelable', fileprovider)
        print(f"PARCELABLE: {parcelable}")
        intent.putExtra(MediaStore.EXTRA_OUTPUT, parcelable)
        PythonActivity.mActivity.startActivityForResult(intent, 0x123)

    def _on_activity_result(self, requestCode, resultCode, intent):
        if requestCode != 0x123:
            "REQUEST CODE INCORRECT"
            return
        android.activity.unbind(on_activity_result=self._on_activity_result)
        if self.on_complete(self.filename):
            print("TRIGGERING REMOVE")
            self._remove(self.filename)

    def _remove(self, fn):
        try:
            remove(fn)
        except OSError:
            pass