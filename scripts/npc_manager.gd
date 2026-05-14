extends Node

signal npc_interacted(npc_id: String)
signal npc_dialogue_finished(npc_id: String)
signal relationship_changed(npc_id: String, old_value: int, new_value: int)

const NPC_DATA = {
	"neighbor_aya": {
		"name": "绫",
		"description": "热心的中年妇人，常送自家种的菜",
		"personality": "温暖、善解人意、爱操心",
		"color": Color(0.9, 0.6, 0.6, 1),
		"default_dialogue": [
			"欢迎来到云村，希望你会喜欢这里。",
			"今天天气真好呢，很适合在村里走走。",
            "后院的菜园长得不错呀，有什么需要帮忙的吗？"
		],
		"gift_reactions": {
			"food": "太谢谢了！我正好需要这个。",
			"flower": "真漂亮，谢谢你的心意。",
			"trash": "这个...我就不收了。"
		},
		"favorite_gifts": ["白菜", "番茄", "草莓"]
	},
	"elder_takeshi": {
		"name": "武志",
		"description": "沉默寡言的老人，喜欢在树下下棋",
		"personality": "沉稳、内敛、思考者",
		"color": Color(0.5, 0.6, 0.8, 1),
		"default_dialogue": [
			"嗯...你来了。",
			"棋局如人生，落子无悔。",
            "云村的云很美，每天都不一样。"
		],
		"gift_reactions": {
			"food": "嗯，留着吧。",
			"flower": "...不错。",
			"trash": "不要浪费在老夫这里。"
		},
		"favorite_gifts": ["苹果", "茶"]
	},
	"shop_keeper_yuki": {
		"name": "雪",
		"description": "经营村里小店的年轻女孩，信息汇聚地",
		"personality": "活泼、好奇、爱八卦",
		"color": Color(0.6, 0.8, 0.9, 1),
		"default_dialogue": [
			"欢迎光临小店！今天想看看什么？",
			"最近村里发生好多有趣的事呢！",
            "你认识村里的人了吗？他们都很有趣的。"
		],
		"gift_reactions": {
			"food": "哇！是我喜欢的！谢谢你！",
			"flower": "好漂亮~我会好好养的！",
			"trash": "这个...还是算了吧。"
		},
		"favorite_gifts": ["葡萄", "草莓", "鲜花"]
	},
	"child_hana": {
		"name": "花",
		"description": "对外面来的人很好奇的小女孩",
		"personality": "活泼、好奇、有点调皮",
		"color": Color(1.0, 0.7, 0.8, 1),
		"default_dialogue": [
			"你是从很远的地方来的吗？",
			"云村外面是什么样的？有大海吗？",
            "大人都很忙，你陪我玩好不好？"
		],
		"gift_reactions": {
			"food": "哇！好吃的！谢谢哥哥/姐姐！",
			"flower": "好漂亮！我要把它画下来！",
			"trash": "这个...好奇怪..."
		},
		"favorite_gifts": ["糖果", "鲜花", "蝴蝶结"]
	}
}

var npcs: Dictionary = {}
var player_relationships: Dictionary = {}

func _ready() -> void:
	init_npcs()
	print("[NPCManager] 云村居民系统初始化完成，共 ", npcs.size(), " 位居民")

func init_npcs() -> void:
	for npc_id in NPC_DATA.keys():
		var data = NPC_DATA[npc_id]
		var npc = create_npc(npc_id, data)
		add_child(npc)
		npcs[npc_id] = npc
		player_relationships[npc_id] = 0

func create_npc(npc_id: String, data: Dictionary) -> CharacterBody2D:
	var npc = CharacterBody2D.new()
	npc.set("npc_id", npc_id)
	npc.set("display_name", data["name"])
	npc.set("description", data["description"])
	npc.set("personality", data["personality"])
	npc.set("npc_color", data["color"])
	npc.set("dialogues", data["default_dialogue"])
	npc.set("current_dialogue_index", 0)
	npc.set("relationship", 0)

	npc.collision_layer = 2
	npc.collision_mask = 3

	var collision = CollisionShape2D.new()
	var shape = RectangleShape2D.new()
	shape.size = Vector2(32, 32)
	collision.shape = shape
	npc.add_child(collision)

	var sprite = ColorRect.new()
	sprite.size = Vector2(32, 32)
	sprite.color = data["color"]
	sprite.position = Vector2(-16, -24)
	npc.add_child(sprite)

	var name_label = Label.new()
	name_label.text = data["name"]
	name_label.position = Vector2(-20, -45)
	name_label.add_theme_color_override("font_color", Color(1, 1, 0.8))
	npc.add_child(name_label)

	npc.add_to_group("npc")
	npc.add_to_group("interactable")

	return npc

func interact(npc_id: String) -> void:
	if not npc_id in npcs:
		return

	var npc = npcs[npc_id]
	var dialogues = npc.get("dialogues", [])
	var index = npc.get("current_dialogue_index", 0) as int

	if dialogues.size() > 0:
		var dialogue = dialogues[index % dialogues.size()]
		var npc_data = NPC_DATA.get(npc_id, {})
		var npc_name = npc_data.get("name", "???")

		if has_node("/root/UIManager"):
			get_node("/root/UIManager").show_dialogue(npc_name, dialogue)

		npc.set("current_dialogue_index", index + 1)
		emit_signal("npc_interacted", npc_id)

func give_gift(npc_id: String, item_type: String) -> bool:
	if not npc_id in npcs:
		return false

	var npc_data = NPC_DATA.get(npc_id, {})
	var reactions = npc_data.get("gift_reactions", {})
	var favorites = npc_data.get("favorite_gifts", [])

	var reaction_key = "trash"
	if item_type in ["白菜", "番茄", "黄瓜", "萝卜", "苹果", "葡萄", "草莓"]:
		reaction_key = "food"
	elif item_type in ["鲜花", "花"]:
		reaction_key = "flower"

	var reaction = reactions.get(reaction_key, "谢谢...")

	if has_node("/root/UIManager"):
		var npc_name = npc_data.get("name", "???")
		get_node("/root/UIManager").show_dialogue(npc_name, reaction)

	if item_type in favorites:
		change_relationship(npc_id, 15)
	else:
		change_relationship(npc_id, 5)

	return true

func change_relationship(npc_id: String, delta: int) -> void:
	var old_value = player_relationships.get(npc_id, 0)
	var new_value = clamp(old_value + delta, -100, 100)
	player_relationships[npc_id] = new_value

	if npcs.has(npc_id):
		npcs[npc_id].set("relationship", new_value)

	emit_signal("relationship_changed", npc_id, old_value, new_value)

func get_relationship(npc_id: String) -> int:
	return player_relationships.get(npc_id, 0)

func get_all_npcs() -> Array:
	return npcs.keys()

func get_npc_position(npc_id: String) -> Vector2:
	if npcs.has(npc_id):
		return npcs[npc_id].global_position
	return Vector2.ZERO
