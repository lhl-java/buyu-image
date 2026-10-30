using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.PackageManager;
using UnityEngine;

namespace Buyu.Editor
{
    /// <summary>
    /// Native PNG import policy for this project's two local UPM artwork packages.
    /// Adding this source does not run a repair job. The normal import callbacks run
    /// when Unity imports a matching PNG; bulk repair requires the explicit menu.
    /// The PNG source is never rewritten. Runtime sprites and pivots belong to BuyuArtLoader.
    /// </summary>
    public sealed class BuyuArtImportSettings : AssetPostprocessor
    {
        private const string ArtPackage = "com.lhl.buyu.art";
        private const string UiPackage = "com.lhl.buyu.ui-designs";
        private const string ArtRoot = "Packages/" + ArtPackage + "/";
        private const string UiRoot = "Packages/" + UiPackage + "/";
        private const string RepairMenu = "Buyu/Repair Native PNG Import Settings (Reimport Packages)";

        // Unity 6000.6 SystemInfo.maxTextureSize documentation caps 2D textures at 16384,
        // even when graphics hardware reports a larger value. Hardware may impose a lower cap.
        // https://docs.unity3d.com/6000.6/Documentation/ScriptReference/SystemInfo-maxTextureSize.html
        private const int UnityTextureLimit = 16384;
        private static readonly string[] PlatformNames = GetPlatformNames();

        private void OnPreprocessTexture()
        {
            if (!IsScopedPng(assetPath))
                return;
            var importer = assetImporter as TextureImporter;
            if (importer == null)
                throw new InvalidOperationException("Buyu PNG does not have a TextureImporter: " + assetPath);

            // Read only the PNG header. This works on the first import, before Unity's
            // GetSourceTextureWidthAndHeight source information is necessarily available.
            var sourceSize = ReadNativePngSize(assetPath);
            ApplyNativeSettings(importer, sourceSize);
        }

        private void OnPostprocessTexture(Texture2D texture)
        {
            if (!IsScopedPng(assetPath))
                return;
            var sourceSize = ReadNativePngSize(assetPath);
            if (texture == null || texture.width != sourceSize.x || texture.height != sourceSize.y)
                throw new InvalidDataException(
                    "Buyu native PNG import failed: " + assetPath + ". Source is " + sourceSize.x +
                    "x" + sourceSize.y + ", imported texture is " +
                    (texture == null ? "missing" : texture.width + "x" + texture.height) +
                    ". Downscaled or padded artwork is not accepted. Check platform and device limits.");
        }

        [MenuItem(RepairMenu)]
        private static void RepairCurrentPackageImports()
        {
            if (!CanRepairCurrentPackageImports())
                throw new InvalidOperationException(
                    "Stop Play mode and wait for Unity compilation/import to finish before repairing Buyu PNG imports.");

            var paths = new List<string>();
            foreach (var path in AssetDatabase.GetAllAssetPaths())
                if (IsScopedPng(path))
                    paths.Add(path);
            paths.Sort(StringComparer.Ordinal);
            if (paths.Count == 0)
            {
                Debug.LogWarning("No PNGs were found in the two Buyu artwork packages. Resolve the local UPM packages first.");
                return;
            }

            var reimportRequested = 0;
            var unchanged = 0;
            var errors = 0;
            var cancelled = false;
            try
            {
                for (var i = 0; i < paths.Count; i++)
                {
                    var path = paths[i];
                    if (EditorUtility.DisplayCancelableProgressBar(
                        "Repair Buyu native PNG imports", path, (float)i / paths.Count))
                    {
                        cancelled = true;
                        break;
                    }

                    try
                    {
                        var importer = AssetImporter.GetAtPath(path) as TextureImporter;
                        if (importer == null)
                            throw new InvalidDataException("No TextureImporter is available for Buyu PNG: " + path);
                        var sourceSize = ReadNativePngSize(path);
                        var before = EditorJsonUtility.ToJson(importer);
                        ApplyNativeSettings(importer, sourceSize);
                        if (before == EditorJsonUtility.ToJson(importer))
                        {
                            unchanged++;
                            continue;
                        }

                        // Deliberately absent from static initializers and import callbacks.
                        // This potentially expensive reimport is only reached from the user menu.
                        importer.SaveAndReimport();
                        reimportRequested++;
                    }
                    catch (Exception error)
                    {
                        errors++;
                        Debug.LogError("Buyu import repair failed for " + path + ": " + error.Message);
                    }
                }
            }
            finally
            {
                EditorUtility.ClearProgressBar();
            }

            Debug.Log("Buyu PNG settings repair " + (cancelled ? "cancelled" : "finished") +
                ": reimport requested for " + reimportRequested + ", already configured " + unchanged +
                ", settings errors " + errors + ", total scoped PNGs " + paths.Count +
                ". Import failures remain explicit in the Console. This operation does not approve artwork, " +
                "animation playback or release readiness.");
        }

        [MenuItem(RepairMenu, true)]
        private static bool CanRepairCurrentPackageImports()
        {
            return !Application.isBatchMode && !EditorApplication.isPlayingOrWillChangePlaymode &&
                   !EditorApplication.isCompiling && !EditorApplication.isUpdating;
        }

        private static void ApplyNativeSettings(TextureImporter importer, Vector2Int sourceSize)
        {
            var maximum = Mathf.Max(32, Mathf.NextPowerOfTwo(Mathf.Max(sourceSize.x, sourceSize.y)));
            importer.textureType = TextureImporterType.Default;
            importer.textureShape = TextureImporterShape.Texture2D;
            importer.spriteImportMode = SpriteImportMode.None;
            importer.npotScale = TextureImporterNPOTScale.None;
            importer.maxTextureSize = maximum;
            importer.textureCompression = TextureImporterCompression.Uncompressed;
            importer.crunchedCompression = false;
            importer.allowAlphaSplitting = false;
            importer.alphaSource = TextureImporterAlphaSource.FromInput;
            // Alpha itself is preserved. Unity dilates RGB into fully transparent texels
            // to prevent bilinear color fringes; invisible RGB is not a pixel-equality claim.
            importer.alphaIsTransparency = true;
            importer.sRGBTexture = true;
            importer.ignorePngGamma = false;
            importer.swizzleR = TextureImporterSwizzle.R;
            importer.swizzleG = TextureImporterSwizzle.G;
            importer.swizzleB = TextureImporterSwizzle.B;
            importer.swizzleA = TextureImporterSwizzle.A;
            importer.filterMode = FilterMode.Bilinear;
            importer.wrapMode = TextureWrapMode.Clamp;
            importer.anisoLevel = 0;
            importer.mipmapEnabled = false;
            importer.streamingMipmaps = false;
            importer.ignoreMipmapLimit = true;
            importer.isReadable = false;
            importer.vtOnly = false;

            var defaults = importer.GetDefaultPlatformTextureSettings();
            defaults.maxTextureSize = maximum;
            defaults.format = TextureImporterFormat.RGBA32;
            defaults.textureCompression = TextureImporterCompression.Uncompressed;
            defaults.crunchedCompression = false;
            defaults.allowsAlphaSplitting = false;
            importer.SetPlatformTextureSettings(defaults);

            // Existing per-platform overrides can silently restore a 1024/2048 cap,
            // RGB-only format or compression. All current named build targets inherit
            // the explicit native RGBA32 defaults for these two packages.
            foreach (var name in PlatformNames)
            {
                var platform = importer.GetPlatformTextureSettings(name);
                if (platform.overridden)
                    importer.ClearPlatformTextureSettings(platform.name);
            }
        }

        private static bool IsScopedPng(string path)
        {
            return !string.IsNullOrEmpty(path) && path.EndsWith(".png", StringComparison.OrdinalIgnoreCase) &&
                   (path.StartsWith(ArtRoot, StringComparison.Ordinal) ||
                    path.StartsWith(UiRoot, StringComparison.Ordinal));
        }

        private static Vector2Int ReadNativePngSize(string path)
        {
            if (!IsScopedPng(path))
                throw new ArgumentException("PNG is outside the two Buyu packages: " + path, nameof(path));
            var package = UnityEditor.PackageManager.PackageInfo.FindForAssetPath(path);
            if (package == null || (package.name != ArtPackage && package.name != UiPackage) ||
                string.IsNullOrEmpty(package.resolvedPath) || string.IsNullOrEmpty(package.assetPath))
                throw new InvalidDataException("Could not resolve the local Buyu package for PNG: " + path);
            var prefix = package.assetPath.TrimEnd('/') + "/";
            if (!path.StartsWith(prefix, StringComparison.Ordinal))
                throw new InvalidDataException("Buyu PNG package path does not match its resolved package: " + path);
            var physicalPath = Path.Combine(package.resolvedPath,
                path.Substring(prefix.Length).Replace('/', Path.DirectorySeparatorChar));

            byte[] header;
            using (var stream = File.OpenRead(physicalPath))
            using (var reader = new BinaryReader(stream))
                header = reader.ReadBytes(26);
            if (header.Length != 26 || header[0] != 137 || header[1] != 80 || header[2] != 78 ||
                header[3] != 71 || header[4] != 13 || header[5] != 10 || header[6] != 26 || header[7] != 10 ||
                ReadBigEndianUInt32(header, 8) != 13 || header[12] != 73 || header[13] != 72 ||
                header[14] != 68 || header[15] != 82)
                throw new InvalidDataException("Buyu source does not have a valid PNG/IHDR header: " + path);

            var width = ReadBigEndianUInt32(header, 16);
            var height = ReadBigEndianUInt32(header, 20);
            if (width == 0 || height == 0 || width > UnityTextureLimit || height > UnityTextureLimit)
                throw new InvalidDataException("Buyu PNG native dimensions " + width + "x" + height +
                    " exceed Unity's supported 2D limit of " + UnityTextureLimit + " or are zero: " + path +
                    ". The PNG must be delivered through a different explicit asset contract; it will not be resized.");
            if (header[24] > 8)
                throw new InvalidDataException("Buyu PNG uses " + header[24] +
                    "-bit channels, which the current native RGBA32 review policy cannot preserve: " + path +
                    ". Do not silently quantize it; define an appropriate format before import.");

            var hardwareLimit = SystemInfo.maxTextureSize;
            // A headless import worker can report zero; the engine cap still applies.
            // When the device reports a limit, fail instead of accepting an automatic shrink.
            if (hardwareLimit > 0 && (width > hardwareLimit || height > hardwareLimit))
                throw new InvalidDataException("Buyu PNG native dimensions " + width + "x" + height +
                    " exceed this graphics device's texture limit of " + hardwareLimit + ": " + path +
                    ". Native art review requires a device that can display the complete source.");
            return new Vector2Int((int)width, (int)height);
        }

        private static uint ReadBigEndianUInt32(byte[] bytes, int offset)
        {
            return ((uint)bytes[offset] << 24) | ((uint)bytes[offset + 1] << 16) |
                   ((uint)bytes[offset + 2] << 8) | bytes[offset + 3];
        }

        private static string[] GetPlatformNames()
        {
            var names = new HashSet<string>(StringComparer.Ordinal)
            {
                NamedBuildTarget.Standalone.TargetName,
                NamedBuildTarget.Server.TargetName
            };
            foreach (BuildTargetGroup group in Enum.GetValues(typeof(BuildTargetGroup)))
            {
                try
                {
                    var target = NamedBuildTarget.FromBuildTargetGroup(group);
                    if (!string.IsNullOrEmpty(target.TargetName))
                        names.Add(target.TargetName);
                }
                catch (ArgumentException)
                {
                    // Removed/obsolete enum values have no current named target.
                }
            }
            var result = new string[names.Count];
            names.CopyTo(result);
            Array.Sort(result, StringComparer.Ordinal);
            return result;
        }
    }
}
