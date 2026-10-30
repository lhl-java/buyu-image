using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

namespace Buyu
{
    /// <summary>A local art integration scene. Art approval is recorded separately.</summary>
    public sealed class BuyuArtReview : MonoBehaviour
    {
        private enum Mode { Motion, Screens, Assets, Cannons, UiStates, Fishing }
        private ArtDatabase database;
        private Dictionary<string, ArtAsset> assets;
        private Dictionary<string, ArtClip> clips;
        private Font font;
        private RectTransform stage;
        private Text information;
        private Text counter;
        private Image stageBackground;
        private BuyuClipPlayer motionPlayer;
        private Image cannonBarrel;
        private RectTransform cannonMuzzle;
        private Mode mode;
        private int selection;
        private bool lightBackground;
        private bool? loopOverride;
        private bool nativeSize;
        private string startupError;
        private readonly List<GameObject> contents = new List<GameObject>();
        private readonly List<DemoFish> demoFish = new List<DemoFish>();
        private readonly List<DemoShot> demoShots = new List<DemoShot>();
        private ArtClip[] swimClips;
        private int cannonIndex;
        private float infoClock;
        private int captures;
        private Text loopLabel;
        private bool acceptanceAngleOverride;
        public void AcceptanceCannonAngle(float degrees)
        { acceptanceAngleOverride = true; cannonBarrel.rectTransform.localRotation = Quaternion.Euler(0,0,degrees); }

        // Explicit acceptance hooks use the same production controls/player as manual review.
        public BuyuClipPlayer AcceptancePlayer { get { return motionPlayer; } }
        public RectTransform AcceptanceStage { get { return stage; } }
        public string AcceptanceError { get { return startupError; } }
        public int AcceptanceCaptures { get { return captures; } }
        public Vector3 AcceptanceMuzzleWorld { get { return cannonMuzzle.position; } }
        public void AcceptanceSelect(string category, int index, bool light = false)
        {
            mode = (Mode)Enum.Parse(typeof(Mode), category);
            selection = index;
            lightBackground = light;
            RefreshContents();
        }
        public void AcceptanceFire() { Fire(); }

        private sealed class DemoFish
        {
            public BuyuClipPlayer player;
            public Image image;
            public ArtClip swim;
            public Vector2 position;
            public float speed;
            public bool capturing;
            public float respawnAt;
            public bool shotQueued;
        }

        private sealed class DemoShot
        {
            public Image image;
            public DemoFish target;
            public Vector2 position;
        }

        private void Start()
        {
            try
            {
                database = BuyuArtLoader.LoadDatabase();
                assets = database.assets.ToDictionary(item => item.id, StringComparer.Ordinal);
                clips = database.clips.ToDictionary(item => item.id, StringComparer.Ordinal);
                font = BuyuArtLoader.LoadFont(database.fontFile);
                swimClips = database.clips.Where(item => item.action == "swim").ToArray();
                CreateInterface();
                ShowMode(Mode.Motion);
            }
            catch (Exception error)
            {
                startupError = error.ToString();
                Debug.LogException(error, this);
            }
        }

        private void CreateInterface()
        {
            var rootObject = new GameObject("Art review canvas", typeof(RectTransform), typeof(Canvas),
                typeof(CanvasScaler), typeof(GraphicRaycaster));
            rootObject.transform.SetParent(transform, false);
            var canvas = rootObject.GetComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            var scaler = rootObject.GetComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1920, 1080);
            scaler.matchWidthOrHeight = .5f;
            var root = rootObject.GetComponent<RectTransform>();
            if (FindAnyObjectByType<EventSystem>() == null)
            {
                var events = new GameObject("Art review input", typeof(EventSystem), typeof(StandaloneInputModule));
                events.transform.SetParent(transform, false);
            }
            var background = Panel(root, "Tool background", new Color(.035f, .09f, .10f));
            background.raycastTarget = false;
            Stretch(background.rectTransform, Vector2.zero, Vector2.zero);
            var logo = Panel(root, "Official game logo", Color.white);
            logo.raycastTarget = false;
            logo.sprite = BuyuArtLoader.LoadSprite(assets[database.logoAssetId]);
            logo.type = Image.Type.Simple;
            var logoRect = logo.rectTransform;
            logoRect.anchorMin = logoRect.anchorMax = new Vector2(0, 1);
            logoRect.pivot = new Vector2(0, 1);
            logoRect.anchoredPosition = new Vector2(28, -4);
            logoRect.sizeDelta = new Vector2(220, 110);
            var heading = Label(root, database.gameName + " · 美术接入验收", new Vector2(280, -30), new Vector2(430, 42), 28);
            heading.font = font;
            Label(root, database.gameArtComplete ? "首发美术已验收 · 证据见 UNITY_FINAL_ACCEPTANCE.json" : "候选资源 · 尚未记录 Unity 动作验收通过", new Vector2(730, -40), new Vector2(1000, 32), 19);
            Button(root, "动作 / 特效", 28, 70, 150, () => ShowMode(Mode.Motion));
            Button(root, "31 张界面设计", 190, 70, 180, () => ShowMode(Mode.Screens));
            Button(root, "独立素材", 382, 70, 140, () => ShowMode(Mode.Assets));
            Button(root, "炮台轴心", 534, 70, 140, () => ShowMode(Mode.Cannons));
            Button(root, "UI 状态", 686, 70, 160, () => ShowMode(Mode.UiStates));
            Button(root, "捕鱼演示", 858, 70, 160, () => ShowMode(Mode.Fishing));
            Button(root, "明暗叠底", 1030, 70, 140, ToggleBackground);
            Button(root, "上一项", 1182, 70, 120, () => MoveSelection(-1));
            Button(root, "下一项", 1314, 70, 120, () => MoveSelection(1));
            Button(root, "参考尺寸 / 1:1", 1446, 70, 220, ToggleNativeSize);
            counter = Label(root, "", new Vector2(1680, -138), new Vector2(210, 38), 20);
            Button(root, "播放 / 暂停", 28, 126, 180, TogglePlayback);
            Button(root, "从首帧重播", 220, 126, 180, () => { if (motionPlayer != null) motionPlayer.Replay(); });
            Button(root, "前一帧", 412, 126, 140, () => Step(-1));
            Button(root, "后一帧", 564, 126, 140, () => Step(1));
            loopLabel = Button(root, "循环：跟随清单", 716, 126, 260, ToggleLoop);
            Button(root, "发射 / 捕获", 988, 126, 200, Fire);
            information = Label(root, "", new Vector2(1208, -186), new Vector2(680, 80), 17);
            stageBackground = Panel(root, "Stage backdrop", new Color(.07f, .15f, .18f));
            stageBackground.raycastTarget = false;
            stage = stageBackground.rectTransform;
            Stretch(stage, new Vector2(28, 28), new Vector2(-28, -280));
            stage.gameObject.AddComponent<RectMask2D>();
            Canvas.ForceUpdateCanvases();
        }

        private void ShowMode(Mode value)
        {
            mode = value;
            selection = 0;
            RefreshContents();
        }

        private void ClearContents()
        {
            foreach (var value in contents)
            {
                if (value == null) continue;
                value.SetActive(false);
                Destroy(value);
            }
            contents.Clear();
            demoFish.Clear();
            demoShots.Clear();
            motionPlayer = null;
            cannonBarrel = null;
            acceptanceAngleOverride = false;
        }

        private void RefreshContents()
        {
            ClearContents();
            stageBackground.color = lightBackground ? new Color(.91f, .88f, .79f) : new Color(.07f, .15f, .18f);
            try
            {
                switch (mode)
                {
                    case Mode.Motion: ShowMotion(); break;
                    case Mode.Screens: ShowScreen(); break;
                    case Mode.Assets: ShowAsset(); break;
                    case Mode.Cannons: ShowCannon(); break;
                    case Mode.UiStates: ShowUiStates(); break;
                    case Mode.Fishing: ShowFishing(); break;
                }
            }
            catch (Exception error)
            {
                information.text = "资源接入错误：" + error.Message;
                Debug.LogException(error, this);
            }
        }

        private void ShowMotion()
        {
            var clip = database.clips[selection];
            var root = clip.actorId == "dao-child" ? new Vector2(.5f, .22f) : new Vector2(.62f, .53f);
            var image = ContentImage("Registered native frames", root);
            motionPlayer = image.gameObject.AddComponent<BuyuClipPlayer>();
            motionPlayer.Target = image;
            motionPlayer.LoopOverride = loopOverride;
            if (nativeSize)
            {
                // A review-only copy of the data. Source frames and approved scale remain unchanged.
                var frames = clip.frames.Select(CopyFrameAtNativeSize).ToArray();
                motionPlayer.SetClip(new ArtClip { id = clip.id, actorId = clip.actorId, action = clip.action,
                    name = clip.name, fps = clip.fps, loop = clip.loop, frames = frames, manifest = clip.manifest });
            }
            else motionPlayer.SetClip(clip);
            RootMarker(root);
            counter.text = (selection + 1) + " / " + database.clips.Length;
            UpdateMotionInformation();
        }

        private static ArtFrame CopyFrameAtNativeSize(ArtFrame frame)
        {
            return new ArtFrame { file = frame.file, width = frame.width, height = frame.height,
                pivotX = frame.pivotX, pivotY = frame.pivotY, displayWidth = frame.width,
                displayHeight = frame.height, durationMs = frame.durationMs, sha256 = frame.sha256,
                alphaBounds = frame.alphaBounds };
        }

        private void ShowScreen()
        {
            var screen = database.screens[selection];
            var frame = new ArtFrame { file = screen.file, width = screen.width, height = screen.height,
                displayWidth = screen.width, displayHeight = screen.height, pivotX = .5f, pivotY = .5f };
            SetStatic(ContentImage(screen.name, new Vector2(.5f, .5f)), frame, !nativeSize);
            counter.text = (selection + 1) + " / " + database.screens.Length;
            information.text = screen.name + " · " + screen.width + " × " + screen.height +
                "\n整屏美术设计参考；可点击功能由独立组件接入。";
        }

        private void ShowAsset()
        {
            var asset = database.assets[selection];
            SetStatic(ContentImage(asset.id, new Vector2(.5f, .5f)),
                nativeSize ? CopyFrameAtNativeSize(asset) : asset, false);
            RootMarker(new Vector2(.5f, .5f));
            counter.text = (selection + 1) + " / " + database.assets.Length;
            information.text = asset.category + " · " + asset.name + "\n" + asset.file + "\n" +
                asset.width + " × " + asset.height + " · " + asset.status;
        }

        private void ShowCannon()
        {
            cannonIndex = selection;
            CreateCannon(new Vector2(.5f, .32f));
            counter.text = (selection + 1) + " / " + database.cannons.Length;
            information.text = database.cannons[selection].name + "\n移动鼠标检查炮管转轴；按左右键切换炮台。";
        }

        private void ShowUiStates()
        {
            if (database.uiFamilies == null || database.uiFamilies.Length == 0)
                throw new InvalidOperationException("Regenerate the Unity database with UI state registration.");
            var family = database.uiFamilies[selection];
            var scale = nativeSize ? 1f : family.sharedDisplayScale;
            for (var i = 0; i < family.states.Length; i++)
            {
                var state = family.states[i];
                var asset = assets[state.assetId];
                var containerObject = new GameObject(family.id + "/" + state.state, typeof(RectTransform));
                containerObject.transform.SetParent(stage, false);
                contents.Add(containerObject);
                var container = containerObject.GetComponent<RectTransform>();
                container.anchorMin = container.anchorMax = new Vector2((i + .5f) / family.states.Length, .64f);
                container.sizeDelta = new Vector2(family.logicalCanvas[0], family.logicalCanvas[1]) * scale;
                var image = Panel(container, "Registered state artwork", Color.white);
                image.raycastTarget = false;
                image.sprite = BuyuArtLoader.LoadSprite(asset);
                var rect = image.rectTransform;
                rect.anchorMin = rect.anchorMax = new Vector2(0, 1);
                rect.pivot = new Vector2(0, 1);
                rect.anchoredPosition = new Vector2(state.drawOffset[0], -state.drawOffset[1]) * scale;
                rect.sizeDelta = new Vector2(asset.width, asset.height) * scale;
                var label = Label(container, state.state,
                    new Vector2((container.sizeDelta.x-180)/2, 58), new Vector2(180, 40), 23);
                label.alignment = TextAnchor.MiddleCenter;
                if (family.id == "primary" || family.id == "secondary" || family.id == "tab")
                {
                    var content = family.contentRect;
                    var live = Label(container, family.id == "primary" ? "开始捕鱼" : family.id == "secondary" ? "领取奖励" : "浅海渔场",
                        new Vector2(content[0], -content[1]) * scale, new Vector2(content[2], content[3]) * scale, 23);
                    live.alignment = TextAnchor.MiddleCenter;
                    live.color = family.id == "primary" || (family.id == "tab" && state.state == "selected") ? new Color(1, .96f, .84f) : new Color(.09f, .24f, .20f);
                }
            }
            for (var i = 0; i < 3; i++)
            {
                var value = new GameObject("Interactive " + family.id, typeof(RectTransform));
                value.transform.SetParent(stage, false);
                contents.Add(value);
                var rect = value.GetComponent<RectTransform>();
                rect.anchorMin = rect.anchorMax = new Vector2((i + 1) * .25f, .20f);
                var control = value.AddComponent<BuyuRegisteredControl>();
                control.Init(family, assets, font, "开始捕鱼", () => { information.text = family.id + " · 实际控件点击事件已触发"; });
                control.Selected = i == 1;
                control.Interactable = i != 2;
                var title = Label(rect, i == 0 ? "按下 / 松开" : i == 1 ? "选中状态" : "禁用状态",
                    new Vector2((rect.sizeDelta.x-180)/2, 46), new Vector2(180, 38), 21);
                title.alignment = TextAnchor.MiddleCenter;
            }
            counter.text = (selection + 1) + " / " + database.uiFamilies.Length;
            information.text = family.id + " · 同一家族统一比例 " + scale.ToString("0.000") +
                "\n使用原生 drawOffset，共享文字安全区；源形状差异与实际切换记录见最终验收。";
        }

        private void CreateCannon(Vector2 position)
        {
            var cannon = database.cannons[cannonIndex];
            SetStatic(ContentImage("Cannon base", position), assets[cannon.baseAssetId], false);
            cannonBarrel = ContentImage("Cannon barrel", position);
            SetStatic(cannonBarrel, assets[cannon.barrelAssetId], false);
            if (cannon.muzzle == null || cannon.muzzle.Length != 2)
                throw new InvalidOperationException("Missing registered cannon mouth: " + cannon.id);
            var marker = new GameObject("Registered muzzle", typeof(RectTransform));
            cannonMuzzle = marker.GetComponent<RectTransform>();
            cannonMuzzle.SetParent(cannonBarrel.transform, false);
            cannonMuzzle.anchorMin = cannonMuzzle.anchorMax = new Vector2(cannon.muzzle[0], 1 - cannon.muzzle[1]);
            cannonMuzzle.anchoredPosition = Vector2.zero;
            if (mode == Mode.Cannons)
            {
                var dot = marker.AddComponent<Image>(); dot.color = new Color(1, .35f, .2f, .9f);
                dot.raycastTarget = false; cannonMuzzle.sizeDelta = new Vector2(6, 6);
            }
            RootMarker(position);
        }

        private void ShowFishing()
        {
            var background = database.assets.FirstOrDefault(a => a.category == "scenes" && a.id.Contains("shallow"));
            if (background != null)
            {
                var sea = ContentImage("Shallow sea", new Vector2(.5f, .5f));
                SetStatic(sea, background, true);
                var cover = Mathf.Max(stage.rect.width / background.width, stage.rect.height / background.height);
                sea.rectTransform.sizeDelta = new Vector2(background.width, background.height) * cover;
            }
            for (var i = 0; i < Math.Min(6, swimClips.Length); i++)
            {
                var clip = swimClips[(selection * 6 + i) % swimClips.Length];
                var image = ContentImage(clip.actorId, new Vector2(.5f, .5f));
                var player = image.gameObject.AddComponent<BuyuClipPlayer>();
                player.Target = image;
                player.SetClip(clip);
                var fish = new DemoFish { player = player, image = image, swim = clip,
                    position = new Vector2(-680 + i * 235, -80 + (i % 3) * 160), speed = 32 + i * 9 };
                demoFish.Add(fish);
            }
            cannonIndex = selection % database.cannons.Length;
            CreateCannon(new Vector2(.5f, .15f));
            counter.text = (selection + 1) + " / " + Math.Max(1, (swimClips.Length + 5) / 6);
            information.text = "离线美术演示 · 点击鱼或发射按钮检查捕获\n已捕获 " + captures + " · 不含联网、经济与付费逻辑";
        }

        private void Capture(DemoFish fish)
        {
            if (mode != Mode.Fishing || fish.capturing || !fish.image.enabled) return;
            ArtClip capture;
            if (!clips.TryGetValue(fish.swim.actorId + "/capture", out capture))
                throw new InvalidOperationException("Missing capture clip for " + fish.swim.actorId);
            fish.capturing = true;
            fish.player.SetClip(capture, true, () =>
            {
                fish.image.enabled = false;
                fish.respawnAt = Time.unscaledTime + 1.2f;
                captures++;
            });
            ArtClip net;
            if (clips.TryGetValue("fx-net", out net))
            {
                var effect = ContentImage("Capture net", new Vector2(.5f, .5f));
                effect.rectTransform.anchoredPosition = BodyCenter(fish);
                var player = effect.gameObject.AddComponent<BuyuClipPlayer>();
                player.Target = effect;
                player.SetClip(net, true, () => { effect.gameObject.SetActive(false); contents.Remove(effect.gameObject); Destroy(effect.gameObject); });
            }
        }

        private void Fire()
        {
            if (mode != Mode.Fishing) return;
            var target = demoFish.FirstOrDefault(fish => !fish.capturing && !fish.shotQueued && fish.image.enabled);
            if (target != null) Shoot(target);
        }

        private Vector2 BodyCenter(DemoFish fish)
        {
            var frame = fish.player.Clip.frames[fish.player.FrameIndex];
            var box = frame.alphaBounds;
            if (box == null || box.Length != 4) return fish.position;
            return fish.position + new Vector2(((box[0] + box[2]) * .5f - frame.pivotX * frame.width) * frame.displayWidth / frame.width,
                (frame.pivotY * frame.height - (box[1] + box[3]) * .5f) * frame.displayHeight / frame.height);
        }

        private void Shoot(DemoFish fish)
        {
            if (fish.capturing || fish.shotQueued || !fish.image.enabled || cannonBarrel == null) return;
            if (database.projectile == null) throw new InvalidOperationException("Missing projectile art metadata.");
            var image = ContentImage("Native projectile", new Vector2(.5f, .5f));
            SetStatic(image, assets[database.projectile.asset], false);
            image.rectTransform.pivot = new Vector2(database.projectile.headAnchor[0], 1 - database.projectile.headAnchor[1]);
            var cannonRoot = Vector2.Scale(cannonBarrel.rectTransform.anchorMin - new Vector2(.5f, .5f), stage.rect.size);
            var direction = BodyCenter(fish) - cannonRoot;
            var angle = Mathf.Atan2(direction.y, direction.x) * Mathf.Rad2Deg;
            cannonBarrel.rectTransform.localRotation = Quaternion.Euler(0, 0, angle - 90);
            // The muzzle is a child of the rotated, native-pivot barrel; no shared nominal offset.
            var position = (Vector2)stage.InverseTransformPoint(cannonMuzzle.position);
            image.rectTransform.anchoredPosition = position;
            demoShots.Add(new DemoShot { image = image, target = fish, position = position });
            fish.shotQueued = true;
        }

        private void Update()
        {
            if (startupError != null || database == null || stage == null) return;
            if (Input.GetKeyDown(KeyCode.LeftArrow)) MoveSelection(-1);
            if (Input.GetKeyDown(KeyCode.RightArrow)) MoveSelection(1);
            if (Input.GetKeyDown(KeyCode.Space)) { if (mode == Mode.Fishing) Fire(); else TogglePlayback(); }
            if (mode == Mode.Fishing && Input.GetMouseButtonDown(0) &&
                (EventSystem.current == null || !EventSystem.current.IsPointerOverGameObject()))
            {
                Vector2 pointer;
                if (RectTransformUtility.ScreenPointToLocalPointInRectangle(stage, Input.mousePosition, null, out pointer))
                {
                    for (var i = demoFish.Count - 1; i >= 0; i--)
                    {
                        var fish = demoFish[i];
                        if (!fish.image.enabled || fish.capturing) continue;
                        var frame = fish.player.Clip.frames[fish.player.FrameIndex];
                        var bounds = frame.alphaBounds;
                        if (bounds == null || bounds.Length != 4) continue;
                        var sx = frame.displayWidth / frame.width;
                        var sy = frame.displayHeight / frame.height;
                        var hit = new Rect(fish.position.x + (bounds[0] - frame.pivotX * frame.width) * sx,
                            fish.position.y + (frame.pivotY * frame.height - bounds[3]) * sy,
                            (bounds[2] - bounds[0]) * sx, (bounds[3] - bounds[1]) * sy);
                        if (hit.Contains(pointer)) { Shoot(fish); break; }
                    }
                }
            }
            if (cannonBarrel != null && !acceptanceAngleOverride)
            {
                Vector2 local;
                if (RectTransformUtility.ScreenPointToLocalPointInRectangle(stage, Input.mousePosition, null, out local))
                {
                    var delta = local - cannonBarrel.rectTransform.anchoredPosition;
                    // anchoredPosition is stage-center based for this target.
                    var rootOffset = Vector2.Scale(cannonBarrel.rectTransform.anchorMin - new Vector2(.5f, .5f), stage.rect.size);
                    delta -= rootOffset;
                    var angle = Mathf.Atan2(delta.y, delta.x) * Mathf.Rad2Deg - 90;
                    cannonBarrel.rectTransform.localRotation = Quaternion.Euler(0, 0, angle);
                }
            }
            foreach (var fish in demoFish)
            {
                if (!fish.capturing)
                {
                    fish.position.x += fish.speed * Time.unscaledDeltaTime;
                    if (fish.position.x > stage.rect.width * .5f + 240) fish.position.x = -stage.rect.width * .5f - 200;
                }
                else if (!fish.image.enabled && Time.unscaledTime >= fish.respawnAt)
                {
                    fish.capturing = false;
                    fish.image.enabled = true;
                    fish.position.x = -stage.rect.width * .5f - 150;
                    fish.player.SetClip(fish.swim);
                }
                fish.image.rectTransform.anchoredPosition = fish.position;
            }
            for (var i = demoShots.Count - 1; i >= 0; i--)
            {
                var shot = demoShots[i];
                var delta = BodyCenter(shot.target) - shot.position;
                var distance = 900f * Time.unscaledDeltaTime;
                if (delta.magnitude <= distance + 12)
                {
                    shot.target.shotQueued = false;
                    Capture(shot.target);
                    contents.Remove(shot.image.gameObject);
                    shot.image.gameObject.SetActive(false);
                    Destroy(shot.image.gameObject);
                    demoShots.RemoveAt(i);
                }
                else
                {
                    shot.position += delta.normalized * distance;
                    shot.image.rectTransform.anchoredPosition = shot.position;
                    var forward = database.projectile.artForward;
                    var artAngle = Mathf.Atan2(-forward[1], forward[0]) * Mathf.Rad2Deg;
                    shot.image.rectTransform.localRotation = Quaternion.Euler(0, 0, Mathf.Atan2(delta.y, delta.x) * Mathf.Rad2Deg - artAngle);
                }
            }
            infoClock += Time.unscaledDeltaTime;
            if (infoClock > .1f)
            {
                infoClock = 0;
                if (mode == Mode.Motion) UpdateMotionInformation();
                else if (mode == Mode.Fishing)
                    information.text = "离线美术演示 · 点击鱼 / 空格发射\n已捕获 " + captures + " · " + demoFish.Count + " 条鱼固定根点播放";
            }
        }

        private void UpdateMotionInformation()
        {
            if (motionPlayer == null || motionPlayer.Clip == null) return;
            var clip = motionPlayer.Clip;
            information.text = clip.name + " · " + clip.fps + " FPS · " + (motionPlayer.FrameIndex + 1) + "/" + clip.frames.Length +
                " · " + (motionPlayer.Playing ? "播放" : "暂停 / 单次结束") + "\n" + clip.id +
                " · 循环 " + (loopOverride.HasValue ? loopOverride.Value.ToString() + "（审片覆盖）" : clip.loop.ToString()) +
                "\n" + (nativeSize ? "原生 1:1；超出舞台部分裁视口" : "清单声明尺寸；保留透明边距与根点");
        }

        private void MoveSelection(int direction)
        {
            var count = mode == Mode.Motion ? database.clips.Length : mode == Mode.Screens ? database.screens.Length :
                mode == Mode.Assets ? database.assets.Length : mode == Mode.Cannons ? database.cannons.Length :
                mode == Mode.UiStates ? database.uiFamilies.Length :
                Math.Max(1, (swimClips.Length + 5) / 6);
            selection = (selection + direction + count) % count;
            RefreshContents();
        }

        private void TogglePlayback()
        {
            if (motionPlayer == null) return;
            if (motionPlayer.Playing) motionPlayer.Pause(); else motionPlayer.Play();
        }

        private void Step(int direction)
        {
            if (motionPlayer == null || motionPlayer.Clip == null) return;
            motionPlayer.Pause();
            motionPlayer.SetFrame((motionPlayer.FrameIndex + direction + motionPlayer.Clip.frames.Length) % motionPlayer.Clip.frames.Length);
        }

        private void ToggleLoop()
        {
            loopOverride = !loopOverride.HasValue ? true : loopOverride.Value ? (bool?)false : null;
            if (loopLabel != null) loopLabel.text = "循环：" + (!loopOverride.HasValue ? "跟随清单" : loopOverride.Value ? "强制循环" : "强制单次");
            if (motionPlayer != null) motionPlayer.LoopOverride = loopOverride;
            UpdateMotionInformation();
        }

        private void ToggleBackground() { lightBackground = !lightBackground; stageBackground.color = lightBackground ? new Color(.91f, .88f, .79f) : new Color(.07f, .15f, .18f); }
        private void ToggleNativeSize() { nativeSize = !nativeSize; if (mode != Mode.Fishing && mode != Mode.Cannons) RefreshContents(); }

        private Image ContentImage(string label, Vector2 anchor)
        {
            var image = Panel(stage, label, Color.white);
            image.raycastTarget = false;
            image.rectTransform.anchorMin = image.rectTransform.anchorMax = anchor;
            image.rectTransform.anchoredPosition = Vector2.zero;
            contents.Add(image.gameObject);
            return image;
        }

        private void SetStatic(Image image, ArtFrame frame, bool fitStage)
        {
            image.sprite = BuyuArtLoader.LoadSprite(frame);
            image.type = Image.Type.Simple;
            image.useSpriteMesh = false;
            image.preserveAspect = false;
            image.rectTransform.pivot = new Vector2(frame.pivotX, 1f - frame.pivotY);
            var size = new Vector2(frame.displayWidth, frame.displayHeight);
            if (fitStage)
            {
                var scale = Mathf.Min(stage.rect.width / frame.width, stage.rect.height / frame.height);
                size = new Vector2(frame.width, frame.height) * Mathf.Min(1, scale);
            }
            image.rectTransform.sizeDelta = size;
        }

        private void RootMarker(Vector2 anchor)
        {
            foreach (var size in new[] { new Vector2(28, 2), new Vector2(2, 28) })
            {
                var marker = ContentImage("Registered root marker", anchor);
                marker.color = new Color(1, .45f, .22f, .9f);
                marker.rectTransform.sizeDelta = size;
            }
        }

        private static Image Panel(Transform parent, string name, Color color)
        {
            var item = new GameObject(name, typeof(RectTransform), typeof(CanvasRenderer), typeof(Image));
            item.transform.SetParent(parent, false);
            var image = item.GetComponent<Image>(); image.color = color;
            return image;
        }

        private Text Label(Transform parent, string text, Vector2 topLeft, Vector2 size, int fontSize)
        {
            var item = new GameObject("Label", typeof(RectTransform), typeof(CanvasRenderer), typeof(Text));
            item.transform.SetParent(parent, false);
            var label = item.GetComponent<Text>();
            label.font = font; label.fontSize = fontSize; label.text = text; label.color = new Color(.94f, .92f, .82f);
            label.raycastTarget = false; label.alignment = TextAnchor.UpperLeft;
            label.horizontalOverflow = HorizontalWrapMode.Wrap; label.verticalOverflow = VerticalWrapMode.Truncate;
            var rect = label.rectTransform;
            rect.anchorMin = rect.anchorMax = new Vector2(0, 1); rect.pivot = new Vector2(0, 1);
            rect.anchoredPosition = topLeft; rect.sizeDelta = size;
            return label;
        }

        private Text Button(Transform parent, string title, float x, float y, float width, Action action)
        {
            // Reserve an additional 60px above the toolbars for the official 2:1 logo.
            y += 60;
            var image = Panel(parent, title, new Color(.10f, .29f, .28f));
            var rect = image.rectTransform; rect.anchorMin = rect.anchorMax = new Vector2(0, 1);
            rect.pivot = new Vector2(0, 1); rect.anchoredPosition = new Vector2(x, -y); rect.sizeDelta = new Vector2(width, 44);
            var button = image.gameObject.AddComponent<Button>();
            button.onClick.AddListener(() => action());
            var label = Label(rect, title, new Vector2(8, -7), new Vector2(width - 16, 32), 21);
            label.alignment = TextAnchor.MiddleCenter;
            return label;
        }

        private static void Stretch(RectTransform rect, Vector2 min, Vector2 max)
        {
            rect.anchorMin = Vector2.zero; rect.anchorMax = Vector2.one; rect.pivot = new Vector2(.5f, .5f);
            rect.offsetMin = min; rect.offsetMax = max;
        }

        private void OnGUI()
        {
            if (startupError != null) GUI.TextArea(new Rect(20, 20, Screen.width - 40, Screen.height - 40), startupError);
        }
    }
}
