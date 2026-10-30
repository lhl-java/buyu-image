using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using UnityEditor;
using UnityEngine;

namespace Buyu.Editor
{
    /// <summary>
    /// Technical import/metadata validation only. This never approves artwork,
    /// motion, loop joins, font rendering or release readiness.
    /// Run only after the exclusive local resource slot has been handed back.
    /// </summary>
    public static class BuyuArtValidation
    {
        private const string SerifFile = "assets/fonts/NotoSerifCJKsc-Regular.otf";
        private const string FontSample = "捕鱼道家青鳍玄冰龙宫邮件组队确认取消渔网元宝金币任务背包角色技能浅海仙港游动捕获攻击怒态庆祝指引0123456789";
        private const float MetadataTolerance = .00002f;
        private const float SpritePixelTolerance = .05f;

        [Serializable]
        private sealed class CheckResult
        {
            public string group;
            public string id;
            public bool passed;
            public string error;
        }

        [Serializable]
        private sealed class Counts
        {
            public int assetsExpected = 924;
            public int assetsObserved;
            public int assetsPassed;
            public int staticAndFxAssetsExpected = 276;
            public int staticAndFxAssetsObserved;
            public int nativeFrameAssetsExpected = 648;
            public int nativeFrameAssetsObserved;
            public int nativeClipsExpected = 81;
            public int nativeClipsObserved;
            public int nativeFramesExpected = 648;
            public int nativeFramesObserved;
            public int nativeLoopClipsExpected = 40;
            public int nativeLoopClipsObserved;
            public int nativeSingleShotClipsExpected = 41;
            public int nativeSingleShotClipsObserved;
            public int fxClipsExpected = 8;
            public int fxClipsObserved;
            public int fxFramesExpected = 128;
            public int fxFramesObserved;
            public int clipsPassed;
            public int screensExpected = 31;
            public int screensObserved;
            public int screensPassed;
            public int uiFamiliesExpected = 8;
            public int uiFamiliesObserved;
            public int uiFamiliesPassed;
            public int uiStatesExpected = 22;
            public int uiStatesObserved;
            public int uiStatesPassed;
            public int fontsExpected = 2;
            public int fontsPassed;
            public int sampleGlyphsPerFont;
            public int textureLoadsVerified;
            public int spritesVerified;
            public int checks;
            public int errors;
        }

        [Serializable]
        private sealed class ValidationReport
        {
            public int schemaVersion = 1;
            public string generatedAt;
            public string unityVersion;
            public bool batchMode;
            public string databaseGeneratedAt;
            public string status = "technical_validation_failed";
            public bool technicalImportPassed;
            public bool manualPlaybackApproved = false;
            public bool loopVisualApproved = false;
            public bool fontRenderApproved = false;
            public bool releaseReady = false;
            public bool gameArtComplete = false;
            public bool candidateStatusUnchanged = true;
            public bool pngHashesRecomputed = false;
            public bool sourcePixelsInspected = false;
            public bool graphicsRendered = false;
            public string scope = "Imported texture dimensions, created Sprite metadata, frame timing/registration, UI placement and sample font character availability. No visual or motion approval.";
            public string fontSample = FontSample;
            public Counts counts = new Counts();
            public List<CheckResult> checks = new List<CheckResult>();
            public List<string> retainedVisualWarnings = new List<string>();
        }

        private sealed class Context
        {
            public readonly ValidationReport report = new ValidationReport();
            public readonly Dictionary<string, ArtAsset> byId = new Dictionary<string, ArtAsset>(StringComparer.Ordinal);
            public readonly Dictionary<string, ArtAsset> byFile = new Dictionary<string, ArtAsset>(StringComparer.Ordinal);
            public readonly HashSet<string> verifiedTextures = new HashSet<string>(StringComparer.Ordinal);
            public readonly HashSet<string> verifiedSpriteFiles = new HashSet<string>(StringComparer.Ordinal);
            public readonly HashSet<string> nativeClipIds = new HashSet<string>(StringComparer.Ordinal);
            public readonly HashSet<string> fxClipIds = new HashSet<string>(StringComparer.Ordinal);
            public readonly HashSet<string> frameFiles = new HashSet<string>(StringComparer.Ordinal);
            public readonly HashSet<string> fishActorIds = new HashSet<string>(StringComparer.Ordinal);
            public readonly HashSet<string> staticFishActorIds = new HashSet<string>(StringComparer.Ordinal);
        }

        [Serializable]
        private sealed class SourceUiRegistration
        {
            public SourceUiFamily[] families;
            public SourceUiWarning[] warnings;
        }

        [Serializable]
        private sealed class SourceUiFamily
        {
            public string id;
            public float[] logicalCanvas;
            public float[] contentRect;
            public float[] hitRect;
            public float sharedDisplayScale;
            public SourceUiState[] states;
        }

        [Serializable]
        private sealed class SourceUiState
        {
            public string state;
            public string assetId;
            public string file;
            public int[] sourceNativeSize;
            public float[] drawOffset;
        }

        [Serializable]
        private sealed class SourceUiWarning
        {
            public string id;
            public string family;
            public string state;
        }

        /// <summary>
        /// Command-line entry: -executeMethod Buyu.Editor.BuyuArtValidation.ValidateAll.
        /// Exits with 0/1 only in batch mode. Interactive use keeps the Editor open.
        /// </summary>
        [MenuItem("Buyu/Validate Imported Art Metadata")]
        public static void ValidateAll()
        {
            var context = new Context();
            var report = context.report;
            report.generatedAt = DateTime.UtcNow.ToString("o");
            report.unityVersion = Application.unityVersion;
            report.batchMode = Application.isBatchMode;
            var output = Path.GetFullPath(Path.Combine(Application.dataPath, "../Logs/BuyuArtValidation.json"));
            var exitCode = 1;
            try
            {
                ArtDatabase database = null;
                if (Check(context, "database", "Buyu/art-database", () =>
                {
                    database = BuyuArtLoader.LoadDatabase();
                    Require(database.assets != null && database.clips != null && database.screens != null && database.uiFamilies != null,
                        "Database needs assets, clips, screens and uiFamilies arrays.");
                    // Completion is an external art-review decision; technical validation neither grants nor revokes it.
                    Require(!string.IsNullOrWhiteSpace(database.gameName), "Database needs an official game name.");
                    report.databaseGeneratedAt = database.generatedAt;
                }))
                {
                    ValidateAssets(context, database);
                    ValidateClips(context, database);
                    ValidateScreens(context, database);
                    ValidateUi(context, database);
                    ValidateFonts(context, database);
                    ValidateCounts(context);
                }
                report.counts.checks = report.checks.Count;
                report.counts.errors = report.checks.Count(item => !item.passed);
                report.technicalImportPassed = report.counts.errors == 0;
                report.status = report.technicalImportPassed
                    ? "technical_import_passed_manual_motion_visual_review_pending"
                    : "technical_import_failed_manual_motion_visual_review_pending";
                exitCode = report.technicalImportPassed ? 0 : 1;
            }
            catch (Exception error)
            {
                report.checks.Add(new CheckResult { group = "validator", id = "unhandled", passed = false, error = error.ToString() });
                report.counts.checks = report.checks.Count;
                report.counts.errors = report.checks.Count(item => !item.passed);
                report.technicalImportPassed = false;
                Debug.LogException(error);
            }
            finally
            {
                try
                {
                    Directory.CreateDirectory(Path.GetDirectoryName(output));
                    File.WriteAllText(output, JsonUtility.ToJson(report, true), new UTF8Encoding(false));
                    if (exitCode == 0) Debug.Log("Buyu technical import validation passed. Motion, loop joins and visual approval remain pending. Report: " + output);
                    else Debug.LogError("Buyu technical import validation failed with " + report.counts.errors + " errors. Report: " + output);
                }
                catch (Exception writeError)
                {
                    exitCode = 1;
                    Debug.LogError("Could not write Buyu validation report: " + output);
                    Debug.LogException(writeError);
                }
                if (Application.isBatchMode) EditorApplication.Exit(exitCode);
            }
        }

        private static void ValidateAssets(Context context, ArtDatabase database)
        {
            var counts = context.report.counts;
            counts.assetsObserved = database.assets.Length;
            foreach (var asset in database.assets)
            {
                var id = asset == null ? "<null>" : asset.id;
                if (asset != null && asset.category == "animations") counts.nativeFrameAssetsObserved++;
                else counts.staticAndFxAssetsObserved++;
                if (asset != null && asset.category == "fish" && !string.IsNullOrWhiteSpace(asset.file))
                    context.staticFishActorIds.Add(Path.GetFileNameWithoutExtension(asset.file));
                if (Check(context, "asset", id, () =>
                {
                    Require(asset != null && !string.IsNullOrWhiteSpace(asset.id), "Asset needs a unique nonempty id.");
                    Require(!context.byId.ContainsKey(asset.id), "Duplicate asset id: " + asset.id);
                    Require(!context.byFile.ContainsKey(asset.file), "Duplicate asset file: " + asset.file);
                    context.byId.Add(asset.id, asset);
                    context.byFile.Add(asset.file, asset);
                    VerifyFrame(context, asset);
                })) counts.assetsPassed++;
            }
        }

        private static void ValidateClips(Context context, ArtDatabase database)
        {
            var counts = context.report.counts;
            foreach (var clip in database.clips)
            {
                var id = clip == null ? "<null>" : clip.id;
                var native = clip != null && !string.IsNullOrWhiteSpace(clip.actorId);
                if (native)
                {
                    counts.nativeClipsObserved++;
                    counts.nativeFramesObserved += clip.frames == null ? 0 : clip.frames.Length;
                    if (clip.loop) counts.nativeLoopClipsObserved++; else counts.nativeSingleShotClipsObserved++;
                }
                else
                {
                    counts.fxClipsObserved++;
                    counts.fxFramesObserved += clip == null || clip.frames == null ? 0 : clip.frames.Length;
                }
                if (Check(context, "clip", id, () => ValidateClip(context, clip, native))) counts.clipsPassed++;
            }
        }

        private static void ValidateClip(Context context, ArtClip clip, bool native)
        {
            Require(clip != null && !string.IsNullOrWhiteSpace(clip.id), "Clip needs an id.");
            Require(clip.frames != null && clip.frames.Length == (native ? 8 : 16), "Expected " + (native ? 8 : 16) + " frames.");
            Require(FinitePositive(clip.fps), "Clip fps must be positive and finite.");
            Require(!string.IsNullOrWhiteSpace(clip.manifest), "Clip needs its source manifest reference.");
            Require(clip.manifest.StartsWith(native ? "assets/animations/" : "assets/fx/", StringComparison.Ordinal) &&
                !clip.manifest.Split('/').Any(part => part == ".." || part == "." || part.Length == 0), "Clip manifest path must be canonical and inside its expected source folder.");
            Require(File.Exists(Path.GetFullPath(Path.Combine(Application.dataPath, "../../..", clip.manifest))), "Clip source manifest does not exist: " + clip.manifest);
            Require((native ? context.nativeClipIds : context.fxClipIds).Add(clip.id), "Duplicate clip id: " + clip.id);
            if (native)
            {
                Require(clip.id == clip.actorId + "/" + clip.action, "Native clip id differs from actorId/action.");
                ValidateActionContract(clip);
                if (clip.actorId != "dao-child") context.fishActorIds.Add(clip.actorId);
            }
            else Require(!clip.loop && Near(clip.fps, 16), "FX clips are 16 FPS single-shot in this batch.");
            var first = clip.frames[0];
            Require(first != null, "First clip frame is null.");
            var scale = first.displayWidth / first.width;
            double totalDuration = 0;
            var localFiles = new HashSet<string>(StringComparer.Ordinal);
            for (var index = 0; index < clip.frames.Length; index++)
            {
                var frame = clip.frames[index];
                Require(frame != null, "Null frame " + index);
                Require(localFiles.Add(frame.file), "Repeated frame file in one clip: " + frame.file);
                Require(context.frameFiles.Add(frame.file), "One frame file belongs to multiple clips: " + frame.file);
                Require(frame.file.StartsWith(native ? "assets/animations/" : "assets/fx/", StringComparison.Ordinal), "Frame is outside its expected animation/FX folder.");
                ArtAsset asset;
                Require(context.byFile.TryGetValue(frame.file, out asset), "Clip frame is absent from the asset catalog: " + frame.file);
                Require(frame.width == first.width && frame.height == first.height, "Clip native canvas changes at frame " + index);
                Require(Near(frame.pivotX, first.pivotX) && Near(frame.pivotY, first.pivotY), "Clip pivot changes at frame " + index);
                Require(Near(frame.displayWidth / frame.width, scale) && Near(frame.displayHeight / frame.height, scale), "Clip display scale changes or aspect ratio is distorted at frame " + index);
                Require(scale > 0 && scale <= 1 + MetadataTolerance, "Clip scale is invalid or upscales the native source.");
                Require(asset.width == frame.width && asset.height == frame.height && Near(asset.pivotX, frame.pivotX) && Near(asset.pivotY, frame.pivotY), "Clip/native asset registration differs at frame " + index);
                Require(Near(asset.displayWidth, frame.displayWidth, .02f) && Near(asset.displayHeight, frame.displayHeight, .02f), "Clip/native asset display dimensions differ at frame " + index);
                if (!string.IsNullOrEmpty(frame.sha256) && !string.IsNullOrEmpty(asset.sha256))
                    Require(string.Equals(frame.sha256, asset.sha256, StringComparison.OrdinalIgnoreCase), "Clip and asset stored SHA256 metadata differ; hashes were not recomputed.");
                Require(!float.IsNaN(frame.durationMs) && !float.IsInfinity(frame.durationMs) && frame.durationMs >= 0, "Invalid frame duration at index " + index);
                var duration = frame.durationMs > 0 ? frame.durationMs : 1000.0 / clip.fps;
                Require(Math.Abs(duration - 1000.0 / clip.fps) <= 1.01, "Frame duration differs from the declared uniform FPS at index " + index);
                totalDuration += duration;
                VerifyFrame(context, frame);
            }
            Require(Math.Abs(totalDuration - clip.frames.Length * 1000.0 / clip.fps) <= 1.51, "Clip total duration differs from declared FPS beyond cumulative rounding allowance.");
        }

        private static void ValidateActionContract(ArtClip clip)
        {
            if (clip.actorId == "dao-child")
            {
                Require(clip.action == "idle" || clip.action == "point" || clip.action == "celebrate", "Unknown guide action.");
                Require(clip.loop == (clip.action == "idle"), "Guide loop flag differs from the production contract.");
                Require(Near(clip.fps, clip.action == "idle" ? 8 : 10), "Guide FPS differs from the production contract.");
                return;
            }
            switch (clip.action)
            {
                case "swim": Require(clip.loop && clip.fps >= 8 && clip.fps <= 12, "Fish swim must loop at 8..12 FPS."); break;
                case "capture": Require(!clip.loop && Near(clip.fps, 12), "Fish capture must be single-shot at 12 FPS."); break;
                case "attack":
                    Require(IsBoss(clip.actorId) && !clip.loop && Near(clip.fps, 10), "Boss attack must be single-shot at 10 FPS."); break;
                case "enrage":
                    Require(IsBoss(clip.actorId) && clip.loop && Near(clip.fps, 8), "Boss enrage must loop at 8 FPS."); break;
                default: throw new InvalidDataException("Unknown native action: " + clip.action);
            }
        }

        private static bool IsBoss(string actorId)
        {
            return actorId == "34-jinlongli" || actorId == "35-longwang" || actorId == "36-xuanjing";
        }

        private static void ValidateScreens(Context context, ArtDatabase database)
        {
            context.report.counts.screensObserved = database.screens.Length;
            var ids = new HashSet<string>(StringComparer.Ordinal);
            foreach (var screen in database.screens)
                if (Check(context, "screen", screen == null ? "<null>" : screen.id, () =>
                {
                    Require(screen != null && !string.IsNullOrWhiteSpace(screen.id) && ids.Add(screen.id), "Screen needs a unique nonempty id.");
                    Require(screen.file.StartsWith("designs/ui/", StringComparison.Ordinal), "Screen must reference its real UI design PNG.");
                    Require(screen.width > 0 && screen.height > 0, "Screen dimensions must be positive.");
                    VerifyTexture(context, screen.file, screen.width, screen.height);
                })) context.report.counts.screensPassed++;
        }

        private static void ValidateUi(Context context, ArtDatabase database)
        {
            var counts = context.report.counts;
            counts.uiFamiliesObserved = database.uiFamilies.Length;
            SourceUiRegistration source = null;
            var sourcePath = Path.GetFullPath(Path.Combine(Application.dataPath, "../../../config/ui-state-registration.json"));
            if (!Check(context, "ui-registration", "source", () =>
            {
                Require(File.Exists(sourcePath), "Source UI registration is missing: " + sourcePath);
                source = JsonUtility.FromJson<SourceUiRegistration>(File.ReadAllText(sourcePath, Encoding.UTF8));
                Require(source != null && source.families != null && source.families.Length == 8, "Source UI registration needs eight families.");
                Require(source.families.Sum(family => family.states == null ? 0 : family.states.Length) == 22, "Source UI registration needs twenty-two states.");
                foreach (var warning in source.warnings ?? new SourceUiWarning[0])
                    context.report.retainedVisualWarnings.Add(warning.id + " · " + warning.family + "/" + warning.state + ": original source shape warning remains pending visual review.");
            })) return;
            var familyIds = new HashSet<string>(StringComparer.Ordinal);
            foreach (var family in database.uiFamilies)
            {
                counts.uiStatesObserved += family == null || family.states == null ? 0 : family.states.Length;
                SourceUiFamily original = null;
                if (!Check(context, "ui-family", family == null ? "<null>" : family.id, () =>
                {
                    Require(family != null && !string.IsNullOrWhiteSpace(family.id) && familyIds.Add(family.id), "UI family needs a unique id.");
                    original = source.families.FirstOrDefault(item => item.id == family.id);
                    Require(original != null, "UI family is absent from source registration.");
                    Require(family.logicalCanvas != null && family.logicalCanvas.Length == 2 && family.logicalCanvas.All(FinitePositive), "UI family needs a positive logical canvas.");
                    Require(ArraysNear(family.logicalCanvas, original.logicalCanvas), "UI logical canvas differs from source registration.");
                    Require(ArraysNear(family.contentRect, original.contentRect) && ArraysNear(family.hitRect, original.hitRect), "UI content/hit rectangle differs from source registration.");
                    ValidateRect(family.contentRect, family.logicalCanvas, "contentRect");
                    ValidateRect(family.hitRect, family.logicalCanvas, "hitRect");
                    Require(FinitePositive(family.sharedDisplayScale) && family.sharedDisplayScale <= 1 && Near(family.sharedDisplayScale, original.sharedDisplayScale), "UI family scale differs from its single source reference scale.");
                    Require(family.states != null && original.states != null && family.states.Length == original.states.Length, "UI family state count differs from source registration.");
                })) continue;
                counts.uiFamiliesPassed++;
                var stateNames = new HashSet<string>(StringComparer.Ordinal);
                foreach (var state in family.states)
                    if (Check(context, "ui-state", family.id + "/" + (state == null ? "<null>" : state.state), () =>
                    {
                        Require(state != null && !string.IsNullOrWhiteSpace(state.state) && stateNames.Add(state.state), "UI state needs a unique state name.");
                        var origin = original.states.FirstOrDefault(item => item.state == state.state);
                        Require(origin != null && state.assetId == origin.assetId, "UI state asset differs from its source registration.");
                        ArtAsset asset;
                        Require(context.byId.TryGetValue(state.assetId, out asset), "UI state asset is missing from native catalog: " + state.assetId);
                        Require(asset.file == origin.file, "UI state source PNG differs from registered original.");
                        Require(origin.sourceNativeSize != null && origin.sourceNativeSize.Length == 2 && asset.width == origin.sourceNativeSize[0] && asset.height == origin.sourceNativeSize[1], "UI state native dimensions differ from original registration.");
                        Require(ArraysNear(state.drawOffset, origin.drawOffset) && state.drawOffset.Length == 2, "UI drawOffset differs from original registration.");
                        Require(state.drawOffset.All(value => !float.IsNaN(value) && !float.IsInfinity(value) && value >= 0 && Near(value, Mathf.Round(value))), "UI drawOffset must use nonnegative integer source placement.");
                        Require(state.drawOffset[0] + asset.width <= family.logicalCanvas[0] + MetadataTolerance && state.drawOffset[1] + asset.height <= family.logicalCanvas[1] + MetadataTolerance, "Full native UI state does not fit the shared logical canvas.");
                        VerifyTexture(context, asset.file, asset.width, asset.height);
                    })) counts.uiStatesPassed++;
            }
        }

        private static void ValidateFonts(Context context, ArtDatabase database)
        {
            context.report.counts.sampleGlyphsPerFont = FontSample.Distinct().Count();
            foreach (var path in new[] { BuyuArtLoader.DefaultFontFile, SerifFile })
                if (Check(context, "font", path, () =>
                {
                    Require(database.fontFile == BuyuArtLoader.DefaultFontFile, "Database body font must use the supplied licensed Noto Sans font.");
                    var font = BuyuArtLoader.LoadFont(path);
                    Require(font != null, "Imported Font is null.");
                    var missing = FontSample.Distinct().Where(character => !font.HasCharacter(character)).ToArray();
                    Require(missing.Length == 0, "Imported font lacks sample characters: " + new string(missing));
                })) context.report.counts.fontsPassed++;
        }

        private static void ValidateCounts(Context context)
        {
            var counts = context.report.counts;
            Check(context, "count", "assets", () => Require(counts.assetsObserved == counts.assetsExpected && counts.nativeFrameAssetsObserved == counts.nativeFrameAssetsExpected && counts.staticAndFxAssetsObserved == counts.staticAndFxAssetsExpected, "Expected 924 assets = 648 native motion frames + 276 static/FX assets."));
            Check(context, "count", "native-clips", () => Require(counts.nativeClipsObserved == counts.nativeClipsExpected && counts.nativeFramesObserved == counts.nativeFramesExpected && context.fishActorIds.Count == 36, "Expected 81 native clips, 648 frames and 36 fish actor IDs."));
            Check(context, "count", "native-loop-flags", () => Require(counts.nativeLoopClipsObserved == counts.nativeLoopClipsExpected && counts.nativeSingleShotClipsObserved == counts.nativeSingleShotClipsExpected, "Expected 40 looping and 41 single-shot native clips."));
            Check(context, "count", "native-actor-roster", () =>
            {
                Require(context.staticFishActorIds.Count == 36 && context.staticFishActorIds.SetEquals(context.fishActorIds), "Native animation actor IDs must match all thirty-six static fish identities.");
                var expected = new HashSet<string>(StringComparer.Ordinal);
                foreach (var actorId in context.staticFishActorIds)
                {
                    expected.Add(actorId + "/swim"); expected.Add(actorId + "/capture");
                    if (IsBoss(actorId)) { expected.Add(actorId + "/attack"); expected.Add(actorId + "/enrage"); }
                }
                expected.Add("dao-child/idle"); expected.Add("dao-child/point"); expected.Add("dao-child/celebrate");
                Require(expected.SetEquals(context.nativeClipIds), "Native action roster differs from fish swim/capture, boss attack/enrage and guide idle/point/celebrate contract.");
            });
            Check(context, "count", "fx-clips", () => Require(counts.fxClipsObserved == counts.fxClipsExpected && counts.fxFramesObserved == counts.fxFramesExpected, "Expected eight FX clips with 128 frames."));
            Check(context, "count", "screens", () => Require(counts.screensObserved == counts.screensExpected, "Expected thirty-one UI design screens."));
            Check(context, "count", "ui-states", () => Require(counts.uiFamiliesObserved == counts.uiFamiliesExpected && counts.uiStatesObserved == counts.uiStatesExpected, "Expected eight UI families and twenty-two states."));
            Check(context, "count", "fonts", () => Require(counts.fontsPassed == counts.fontsExpected, "Both supplied Noto fonts must load and contain sample characters."));
            Check(context, "count", "frame-coverage", () => Require(context.frameFiles.Count == counts.nativeFramesExpected + counts.fxFramesExpected, "Expected 776 uniquely referenced motion/FX frame files."));
        }

        private static void VerifyFrame(Context context, ArtFrame frame)
        {
            var sprite = BuyuArtLoader.LoadSprite(frame);
            VerifyTexture(context, frame.file, frame.width, frame.height);
            Require(sprite != null && sprite.texture != null, "Created Sprite or texture is null.");
            Require(Near(sprite.rect.x, 0, SpritePixelTolerance) && Near(sprite.rect.y, 0, SpritePixelTolerance) && Near(sprite.rect.width, frame.width, SpritePixelTolerance) && Near(sprite.rect.height, frame.height, SpritePixelTolerance), "Created Sprite rect does not cover the complete native canvas.");
            Require(Near(sprite.pivot.x, frame.pivotX * frame.width, SpritePixelTolerance) && Near(sprite.pivot.y, (1 - frame.pivotY) * frame.height, SpritePixelTolerance), "Created Sprite pivot differs from top-left metadata converted once to Unity coordinates.");
            Require(Near(sprite.pixelsPerUnit, 100, MetadataTolerance), "Created Sprite does not use the shared 100 pixels-per-unit contract.");
            var asset = frame as ArtAsset;
            var borders = asset == null || asset.nineSlice == null || asset.nineSlice.Length == 0
                ? Vector4.zero : new Vector4(asset.nineSlice[0], asset.nineSlice[1], asset.nineSlice[2], asset.nineSlice[3]);
            Require((sprite.border - borders).sqrMagnitude <= SpritePixelTolerance * SpritePixelTolerance, "Created Sprite border differs from the database's Unity L,B,R,T order; border metadata approval remains separate.");
            context.verifiedSpriteFiles.Add(frame.file);
            context.report.counts.spritesVerified = context.verifiedSpriteFiles.Count;
        }

        private static void VerifyTexture(Context context, string file, int width, int height)
        {
            var texture = BuyuArtLoader.LoadTexture(file);
            Require(texture != null && texture.width == width && texture.height == height, "Imported texture dimensions differ from native metadata: " + file + "; observed " + (texture == null ? "null" : texture.width + "x" + texture.height) + ", expected " + width + "x" + height);
            context.verifiedTextures.Add(file);
            context.report.counts.textureLoadsVerified = context.verifiedTextures.Count;
        }

        private static void ValidateRect(float[] rect, float[] canvas, string label)
        {
            Require(rect != null && rect.Length == 4 && rect.All(value => !float.IsNaN(value) && !float.IsInfinity(value) && value >= 0), label + " must have four finite nonnegative values.");
            Require(rect[2] > 0 && rect[3] > 0 && rect[0] + rect[2] <= canvas[0] + MetadataTolerance && rect[1] + rect[3] <= canvas[1] + MetadataTolerance, label + " lies outside its logical canvas.");
        }

        private static bool ArraysNear(float[] left, float[] right)
        {
            return left != null && right != null && left.Length == right.Length && left.Where((value, index) => !Near(value, right[index])).Count() == 0;
        }

        private static bool Near(float left, float right, float tolerance = MetadataTolerance)
        {
            return !float.IsNaN(left) && !float.IsInfinity(left) && !float.IsNaN(right) && !float.IsInfinity(right) && Mathf.Abs(left - right) <= tolerance;
        }

        private static bool FinitePositive(float value)
        {
            return !float.IsNaN(value) && !float.IsInfinity(value) && value > 0;
        }

        private static void Require(bool condition, string message)
        {
            if (!condition) throw new InvalidDataException(message);
        }

        private static bool Check(Context context, string group, string id, Action action)
        {
            var result = new CheckResult { group = group, id = id };
            try { action(); result.passed = true; }
            catch (Exception error) { result.passed = false; result.error = error.ToString(); }
            context.report.checks.Add(result);
            return result.passed;
        }
    }
}
