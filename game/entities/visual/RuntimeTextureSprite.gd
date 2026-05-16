class_name RuntimeTextureSprite
extends Sprite2D

@export_file("*.png") var texture_path: String = ""


func _ready() -> void:
	refresh_texture()


func refresh_texture() -> bool:
	texture = _load_texture(texture_path)
	return texture != null


func _load_texture(path: String) -> Texture2D:
	if path.is_empty():
		return null
	if ResourceLoader.exists(path):
		return load(path) as Texture2D
	if FileAccess.file_exists(path):
		var image := Image.load_from_file(path)
		if image != null and not image.is_empty():
			return ImageTexture.create_from_image(image)
	return null
