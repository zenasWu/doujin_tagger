from doujin_tagger.util import translate_errors
from doujin_tagger.audio import AudioFile, AudioFileError
from doujin_tagger.mp4_patch import MP4, MP4Cover


class MP4File(AudioFile, ext=["mp4", "m4a", "m4v", "3gp", "3g2", "3gp2"]):
    translate = {
        "\xa9nam": "title",
        "\xa9alb": "album",
        "\xa9ART": "artist",
        "\xa9day": "date",
        "----:com.apple.iTunes:TAGS": "tags",
        "----:com.apple.iTunes:DOUJIN": "doujin",
        "----:com.apple.iTunes:MAKER": "maker",
        "----:com.apple.iTunes:NSFW": "nsfw", }
    rtranslate = {v: k for k, v in translate.items()}

    def __init__(self, filename):
        super().__init__(filename=filename)
        with translate_errors():
            self.audio = MP4(self["filename"])

    def save(self):
        for key in self:
            try:
                name = self.rtranslate[key]
            except KeyError:
                continue
            values = self.tolist(key)
            if name.startswith("----"):
                values = list(map(lambda v: v.encode("utf-8"), values))
            self.audio[name] = values

        with translate_errors():
            self.audio.save()

    def delete_all_tags(self):
        self.audio.delete()

    def set_image(self, image):
        with image:
            if image.mime_type == "image/jpeg":
                image_format = MP4Cover.FORMAT_JPEG
            elif image.mime_type == "image/png":
                image_format = MP4Cover.FORMAT_PNG
            else:
                raise AudioFileError(
                    f"mp4: Unsupported image format {image.mimi_type}")
            cover = MP4Cover(image.read(), image_format)
            self.audio["covr"] = [cover]
