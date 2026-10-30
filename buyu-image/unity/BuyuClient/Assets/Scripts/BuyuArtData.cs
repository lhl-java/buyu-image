using System;

namespace Buyu
{
    [Serializable]
    public class ArtFrame
    {
        public string file;
        public int width;
        public int height;
        // Artwork metadata uses top-left normalized pivots. Convert Y for Unity.
        public float pivotX = .5f;
        public float pivotY = .5f;
        public float displayWidth;
        public float displayHeight;
        public float durationMs;
        public string sha256;
        // Optional native alpha bounds L,T,R,B; used for coarse demo hit testing only.
        public float[] alphaBounds;
    }

    [Serializable]
    public class ArtAsset : ArtFrame
    {
        public string id;
        public string name;
        public string category;
        public string status;
        // Unity pixel borders: left, bottom, right, top. The exporter converts source L,T,R,B.
        public float[] nineSlice;
    }

    [Serializable]
    public class ArtClip
    {
        public string id;
        public string actorId;
        public string action;
        public string name;
        public float fps;
        public bool loop;
        public string status;
        public string manifest;
        public ArtFrame[] frames;
    }

    [Serializable]
    public class ArtScreen
    {
        public string id;
        public string name;
        public string file;
        public int width;
        public int height;
    }

    [Serializable]
    public class ArtCannon
    {
        public string id;
        public string name;
        public string baseAssetId;
        public string barrelAssetId;
        // Source top-left normalized centre of the visible barrel opening.
        public float[] muzzle;
    }

    [Serializable]
    public class ArtUiState
    {
        public string state;
        public string assetId;
        public float[] drawOffset;
    }

    [Serializable]
    public class ArtUiFamily
    {
        public string id;
        public float[] logicalCanvas;
        public float[] contentRect;
        public float[] hitRect;
        public float sharedDisplayScale;
        public ArtUiState[] states;
    }

    [Serializable]
    public class ArtProjectile
    {
        public string asset;
        public float[] headAnchor;
        public float[] artForward;
    }

    [Serializable]
    public class ArtDatabase
    {
        public string generatedAt;
        public string status;
        public bool gameArtComplete;
        public string fontFile;
        public string gameName;
        public string logoAssetId;
        public ArtAsset[] assets;
        public ArtClip[] clips;
        public ArtScreen[] screens;
        public ArtCannon[] cannons;
        public ArtUiFamily[] uiFamilies;
        public ArtProjectile projectile;
    }
}
