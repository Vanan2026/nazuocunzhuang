extends Node

var bgm_player: AudioStreamPlayer
var ambient_player: AudioStreamPlayer
var sfx_player: AudioStreamPlayer

var current_bgm: String = ""
var is_muted: bool = false
var volume: float = 0.8
var _active_tweens: Array[Tween] = []

func _ready() -> void:
    setup_players()
    print('[AudioManager] 闊抽绯荤粺宸插垵濮嬪寲')

func setup_players() -> void:
    bgm_player = AudioStreamPlayer.new()
    bgm_player.volume_db = linear_to_db(volume)
    add_child(bgm_player)

    ambient_player = AudioStreamPlayer.new()
    ambient_player.volume_db = linear_to_db(volume * 0.6)
    add_child(ambient_player)

    sfx_player = AudioStreamPlayer.new()
    sfx_player.volume_db = linear_to_db(volume)
    add_child(sfx_player)

func play_bgm(path: String, fade_in: bool = true) -> void:
    if path == current_bgm and bgm_player.playing:
        return
    
    var stream = load(path) as AudioStream
    if not stream:
        print('[AudioManager] 鏃犳硶鍔犺浇BGM: ', path)
        return
    
    if fade_in:
        var target_vol = linear_to_db(volume)
        bgm_player.volume_db = -80
        bgm_player.stream = stream
        bgm_player.play()
        
        var tween = create_tween()
        _active_tweens.append(tween)
        tween.tween_property(bgm_player, "volume_db", target_vol, 2.0)
    else:
        bgm_player.stream = stream
        bgm_player.play()
    
    current_bgm = path
    print('[AudioManager] 鎾斁BGM: ', path)

func stop_bgm(fade_out: bool = true) -> void:
    if fade_out and bgm_player.playing:
        var tween = create_tween()
        _active_tweens.append(tween)
        tween.tween_property(bgm_player, "volume_db", -80, 1.5)
        tween.tween_callback(bgm_player.stop)
        tween.tween_callback(func(): current_bgm = "")
    else:
        bgm_player.stop()
        current_bgm = ""

func play_ambient(path: String) -> void:
    var stream = load(path) as AudioStream
    if stream:
        ambient_player.stream = stream
        ambient_player.play()

func play_sfx(path: String, volume_mod: float = 1.0) -> void:
    var stream = load(path) as AudioStream
    if stream:
        sfx_player.volume_db = linear_to_db(volume * volume_mod)
        sfx_player.stream = stream
        sfx_player.play()

func set_volume(v: float) -> void:
    volume = clamp(v, 0.0, 1.0)
    bgm_player.volume_db = linear_to_db(volume)

func mute() -> void:
    is_muted = true
    bgm_player.volume_db = -80

func unmute() -> void:
    is_muted = false
    bgm_player.volume_db = linear_to_db(volume)

func toggle_mute() -> void:
    if is_muted:
        unmute()
    else:
        mute()

func cleanup_for_headless() -> void:
    _kill_audio_tweens()
    _release_player(bgm_player)
    _release_player(ambient_player)
    _release_player(sfx_player)
    current_bgm = ""

func _kill_audio_tweens() -> void:
    for tween in _active_tweens:
        if tween != null and tween.is_valid():
            tween.kill()
    _active_tweens.clear()

func _release_player(player: AudioStreamPlayer) -> void:
    if player == null:
        return
    player.stop()
    player.stream = null

func _input(event: InputEvent) -> void:
    if event.is_action_pressed("volume_up"):
        set_volume(volume + 0.1)
    elif event.is_action_pressed("volume_down"):
        set_volume(volume - 0.1)
