using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
#if UNITY_EDITOR
using UnityEditor;
#endif

namespace Buyu
{
    /// <summary>
    /// Loads the review database and original artwork. Editor artwork comes from the
    /// two local UPM packages. Standalone PNGs require a separate export to
    /// StreamingAssets/BuyuArt, preserving their original relative paths.
    /// Call these Unity object APIs on the main thread.
    /// </summary>
    public static class BuyuArtLoader
    {
        public const string DefaultFontFile = "assets/fonts/NotoSansCJKsc-Regular.otf";
        private const string DatabaseResource = "Buyu/art-database";
        private const string ArtPrefix = "assets/";
        private const string UiPrefix = "designs/ui/";

        private static ArtDatabase database;
        private static readonly Dictionary<string, Texture2D> Textures =
            new Dictionary<string, Texture2D>(StringComparer.Ordinal);
        private static readonly Dictionary<string, Font> Fonts =
            new Dictionary<string, Font>(StringComparer.Ordinal);
        private static readonly Dictionary<SpriteKey, Sprite> Sprites =
            new Dictionary<SpriteKey, Sprite>();
        // Imported textures and fonts are persistent Unity assets and are never destroyed here.
        private static readonly HashSet<Texture2D> OwnedTextures = new HashSet<Texture2D>();

        public static ArtDatabase LoadDatabase()
        {
            if (database != null)
                return database;

            var json = Resources.Load<TextAsset>(DatabaseResource);
            if (json == null || string.IsNullOrWhiteSpace(json.text))
                throw new FileNotFoundException(
                    "Buyu art database is missing or empty: Assets/Resources/" +
                    DatabaseResource + ".json. Generate it before entering Play mode.");

            ArtDatabase parsed;
            try
            {
                parsed = JsonUtility.FromJson<ArtDatabase>(json.text);
            }
            catch (Exception error)
            {
                throw new InvalidDataException("Could not parse Buyu art-database.json.", error);
            }

            if (parsed == null || parsed.assets == null || parsed.clips == null ||
                parsed.screens == null || parsed.cannons == null ||
                string.IsNullOrWhiteSpace(parsed.fontFile))
                throw new InvalidDataException(
                    "Buyu art database must contain assets, clips, screens, cannons and fontFile.");

            database = parsed;
            return database;
        }

        public static Texture2D LoadTexture(string file)
        {
            var relativePath = NormalizeArtPath(file);
            Texture2D texture;
            if (Textures.TryGetValue(relativePath, out texture) && texture != null)
                return texture;

#if UNITY_EDITOR
            var packagePath = ToEditorPackagePath(relativePath);
            texture = AssetDatabase.LoadAssetAtPath<Texture2D>(packagePath);
            if (texture == null)
                throw new FileNotFoundException(
                    "Buyu texture was not imported from the local UPM package: " + packagePath,
                    packagePath);
#else
            var exportedPath = ToStreamingAssetsPath(relativePath);
            if (!File.Exists(exportedPath))
                throw new FileNotFoundException(
                    "Buyu standalone PNG export is missing. Export original artwork to " +
                    "StreamingAssets/BuyuArt/<original-relative-path>: " + exportedPath,
                    exportedPath);

            texture = new Texture2D(2, 2, TextureFormat.RGBA32, false, false);
            texture.name = relativePath;
            texture.hideFlags = HideFlags.DontSave;
            try
            {
                if (!ImageConversion.LoadImage(texture, File.ReadAllBytes(exportedPath), true))
                    throw new InvalidDataException("Could not decode Buyu PNG: " + exportedPath);
                texture.filterMode = FilterMode.Bilinear;
                texture.wrapMode = TextureWrapMode.Clamp;
            }
            catch
            {
                DestroyOwnedObject(texture);
                throw;
            }
            OwnedTextures.Add(texture);
#endif
            Textures[relativePath] = texture;
            return texture;
        }

        public static Sprite LoadSprite(ArtFrame frame)
        {
            ValidateFrame(frame);
            var relativePath = NormalizeArtPath(frame.file);
            var border = GetBorder(frame);
            var key = new SpriteKey(relativePath, frame, border);
            Sprite sprite;
            if (Sprites.TryGetValue(key, out sprite) && sprite != null)
                return sprite;

            var texture = LoadTexture(relativePath);
            if (texture.width != frame.width || texture.height != frame.height)
                throw new InvalidDataException(
                    "Buyu texture dimensions differ from the native frame metadata for " +
                    relativePath + ": texture " + texture.width + "x" + texture.height +
                    ", metadata " + frame.width + "x" + frame.height +
                    ". Check Unity import max size, NPOT scaling and the source file; " +
                    "this loader does not resize or fit artwork.");

            sprite = Sprite.Create(texture, new Rect(0, 0, frame.width, frame.height),
                new Vector2(frame.pivotX, 1f - frame.pivotY), 100f, 0,
                SpriteMeshType.FullRect, border, false);
            if (sprite == null)
                throw new InvalidOperationException("Unity could not create Buyu sprite: " + relativePath);
            sprite.name = relativePath;
            sprite.hideFlags = HideFlags.DontSave;
            Sprites[key] = sprite;
            return sprite;
        }

        public static Font LoadFont(string file)
        {
            var relativePath = NormalizeArtPath(file);
            if (!relativePath.StartsWith("assets/fonts/", StringComparison.Ordinal))
                throw new ArgumentException("Buyu font must reference assets/fonts/: " + file, nameof(file));

            Font font;
            if (Fonts.TryGetValue(relativePath, out font) && font != null)
                return font;
#if UNITY_EDITOR
            var packagePath = ToEditorPackagePath(relativePath);
            font = AssetDatabase.LoadAssetAtPath<Font>(packagePath);
            if (font == null)
                throw new FileNotFoundException(
                    "Buyu bundled font was not imported from the local UPM package: " + packagePath,
                    packagePath);
#else
            // Font(string) does not document raw OTF file decoding. A standalone export
            // must include the same licensed font as an imported Unity Font resource.
            var resourcePath = "Buyu/Fonts/" + Path.GetFileNameWithoutExtension(relativePath);
            font = Resources.Load<Font>(resourcePath);
            if (font == null)
                throw new FileNotFoundException(
                    "Buyu standalone font export is missing: Resources/" + resourcePath +
                    ". Import the licensed bundled OTF into that resource path when exporting " +
                    "the standalone client. Copying only raw OTF bytes to " +
                    ToStreamingAssetsPath(relativePath) + " does not create a Unity Font asset.");
#endif
            Fonts[relativePath] = font;
            return font;
        }

        /// <summary>Invalidates generated sprites. Call only when no visible Image uses them.</summary>
        public static void ClearSpriteCache()
        {
            foreach (var sprite in Sprites.Values)
                DestroyOwnedObject(sprite);
            Sprites.Clear();
        }

        /// <summary>
        /// Releases objects created by this loader and drops references to imported assets.
        /// Imported textures and fonts are never destroyed. Rebind visible Images afterwards.
        /// </summary>
        public static void ClearCaches()
        {
            ClearSpriteCache();
            foreach (var texture in OwnedTextures)
                DestroyOwnedObject(texture);
            OwnedTextures.Clear();
            Textures.Clear();
            Fonts.Clear();
            database = null;
        }

        internal static void ValidateFrame(ArtFrame frame)
        {
            if (frame == null)
                throw new ArgumentNullException(nameof(frame), "Buyu frame metadata is null.");
            NormalizeArtPath(frame.file);
            if (frame.width <= 0 || frame.height <= 0)
                throw new InvalidDataException("Buyu frame needs positive native dimensions: " + frame.file);
            if (!IsFinite(frame.pivotX) || !IsFinite(frame.pivotY) ||
                frame.pivotX < 0f || frame.pivotX > 1f || frame.pivotY < 0f || frame.pivotY > 1f)
                throw new InvalidDataException("Buyu frame needs a normalized top-left pivot: " + frame.file);
            if (!IsFinite(frame.displayWidth) || !IsFinite(frame.displayHeight) ||
                frame.displayWidth <= 0f || frame.displayHeight <= 0f)
                throw new InvalidDataException("Buyu frame needs positive display dimensions: " + frame.file);
        }

        private static Vector4 GetBorder(ArtFrame frame)
        {
            var asset = frame as ArtAsset;
            if (asset == null || asset.nineSlice == null || asset.nineSlice.Length == 0)
                return Vector4.zero;
            if (asset.nineSlice.Length != 4)
                throw new InvalidDataException("Buyu nineSlice must have four border values: " + frame.file);
            for (var i = 0; i < 4; i++)
                if (!IsFinite(asset.nineSlice[i]) || asset.nineSlice[i] < 0f)
                    throw new InvalidDataException("Buyu nineSlice has an invalid border: " + frame.file);
            // The database contract uses Unity's pixel border order: left, bottom, right, top.
            var border = new Vector4(asset.nineSlice[0], asset.nineSlice[1],
                asset.nineSlice[2], asset.nineSlice[3]);
            if (border.x + border.z > frame.width || border.y + border.w > frame.height)
                throw new InvalidDataException("Buyu nineSlice exceeds native frame size: " + frame.file);
            return border;
        }

        private static string NormalizeArtPath(string file)
        {
            if (string.IsNullOrWhiteSpace(file))
                throw new ArgumentException("Buyu artwork path is empty.", nameof(file));
            var path = file.Trim().Replace('\\', '/');
            if (!path.StartsWith(ArtPrefix, StringComparison.Ordinal) &&
                !path.StartsWith(UiPrefix, StringComparison.Ordinal))
                throw new ArgumentException(
                    "Buyu artwork must use a project-relative assets/... or designs/ui/... path: " + file,
                    nameof(file));
            foreach (var segment in path.Split('/'))
                if (segment.Length == 0 || segment == "." || segment == ".." || segment.IndexOf(':') >= 0)
                    throw new ArgumentException("Buyu artwork path is not canonical: " + file, nameof(file));
            return path;
        }

#if UNITY_EDITOR
        private static string ToEditorPackagePath(string relativePath)
        {
            return relativePath.StartsWith(ArtPrefix, StringComparison.Ordinal)
                ? "Packages/com.lhl.buyu.art/" + relativePath.Substring(ArtPrefix.Length)
                : "Packages/com.lhl.buyu.ui-designs/" + relativePath.Substring(UiPrefix.Length);
        }
#else
        private static string ToStreamingAssetsPath(string relativePath)
        {
            var root = Application.streamingAssetsPath;
            if (root.Contains("://") || root.StartsWith("jar:", StringComparison.Ordinal))
                throw new PlatformNotSupportedException(
                    "Buyu synchronous art loader currently supports Editor and desktop file-based " +
                    "StreamingAssets. This platform requires a separately implemented asynchronous export loader.");
            return Path.Combine(root, "BuyuArt", relativePath.Replace('/', Path.DirectorySeparatorChar));
        }
#endif

        private static bool IsFinite(float value)
        {
            return !float.IsNaN(value) && !float.IsInfinity(value);
        }

        private static void DestroyOwnedObject(UnityEngine.Object value)
        {
            if (value == null)
                return;
            if (Application.isPlaying)
                UnityEngine.Object.Destroy(value);
            else
                UnityEngine.Object.DestroyImmediate(value);
        }

        private struct SpriteKey : IEquatable<SpriteKey>
        {
            private readonly string file;
            private readonly int width;
            private readonly int height;
            private readonly float pivotX;
            private readonly float pivotY;
            private readonly Vector4 border;

            public SpriteKey(string file, ArtFrame frame, Vector4 border)
            {
                this.file = file;
                width = frame.width;
                height = frame.height;
                pivotX = frame.pivotX;
                pivotY = frame.pivotY;
                this.border = border;
            }

            public bool Equals(SpriteKey other)
            {
                return file == other.file && width == other.width && height == other.height &&
                       pivotX.Equals(other.pivotX) && pivotY.Equals(other.pivotY) && border.Equals(other.border);
            }

            public override bool Equals(object obj)
            {
                return obj is SpriteKey && Equals((SpriteKey)obj);
            }

            public override int GetHashCode()
            {
                unchecked
                {
                    var hash = file.GetHashCode();
                    hash = hash * 397 ^ width;
                    hash = hash * 397 ^ height;
                    hash = hash * 397 ^ pivotX.GetHashCode();
                    hash = hash * 397 ^ pivotY.GetHashCode();
                    return hash * 397 ^ border.GetHashCode();
                }
            }
        }
    }
}
