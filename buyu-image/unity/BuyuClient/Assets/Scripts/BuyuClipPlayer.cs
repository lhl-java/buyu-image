using System;
using System.IO;
using UnityEngine;
using UnityEngine.UI;

namespace Buyu
{
    /// <summary>
    /// Plays native fixed-canvas frames without fitting their alpha bounds.
    /// Use a dedicated Image with fixed anchors, outside any layout that overrides its size.
    /// Disabling this component freezes its clock; enabling it resumes without catching up.
    /// </summary>
    [DisallowMultipleComponent]
    public sealed class BuyuClipPlayer : MonoBehaviour
    {
        [SerializeField] private Image target;
        private ArtClip clip;
        private int frameIndex = -1;
        private bool playing;
        private bool completionSent;
        private Action onComplete;
        private double[] durationsMs;
        private double cycleDurationMs;
        private double elapsedInFrameMs;
        private double lastClockSeconds;

        public bool Playing { get { return playing; } }
        public int FrameIndex { get { return frameIndex; } }
        public ArtClip Clip { get { return clip; } }

        /// <summary>Null follows clip.loop; true/false overrides it for this player.</summary>
        public bool? LoopOverride { get; set; }

        public Image Target
        {
            get { return target; }
            set
            {
                if (value == null)
                    throw new ArgumentNullException(nameof(value), "Buyu clip target Image is missing.");
                target = value;
                if (clip != null && frameIndex >= 0)
                    RenderFrame(clip.frames[frameIndex]);
            }
        }

        private void Awake()
        {
            if (target == null)
                target = GetComponent<Image>();
        }

        private void OnEnable()
        {
            lastClockSeconds = Time.unscaledTimeAsDouble;
        }

        public void SetClip(ArtClip value, bool autoPlay = true, Action onComplete = null)
        {
            if (value == null)
                throw new ArgumentNullException(nameof(value), "Buyu clip metadata is null.");
            if (value.frames == null || value.frames.Length == 0)
                throw new InvalidDataException("Buyu clip contains no frames: " + value.id);

            var preparedDurations = new double[value.frames.Length];
            double total = 0;
            for (var i = 0; i < value.frames.Length; i++)
            {
                var frame = value.frames[i];
                BuyuArtLoader.ValidateFrame(frame);
                if (float.IsNaN(frame.durationMs) || float.IsInfinity(frame.durationMs) || frame.durationMs < 0f)
                    throw new InvalidDataException("Buyu frame has invalid durationMs: " + frame.file);
                var duration = (double)frame.durationMs;
                if (duration == 0)
                {
                    if (float.IsNaN(value.fps) || float.IsInfinity(value.fps) || value.fps <= 0f)
                        throw new InvalidDataException(
                            "Buyu frame has no duration and clip fps is invalid: " + value.id + ", frame " + i);
                    duration = 1000.0 / value.fps;
                }
                preparedDurations[i] = duration;
                total += duration;
            }
            if (double.IsNaN(total) || double.IsInfinity(total) || total <= 0)
                throw new InvalidDataException("Buyu clip has an invalid total duration: " + value.id);

            // Resolve the first frame before replacing a currently visible clip.
            RenderFrame(value.frames[0]);
            clip = value;
            durationsMs = preparedDurations;
            cycleDurationMs = total;
            frameIndex = 0;
            elapsedInFrameMs = 0;
            completionSent = false;
            this.onComplete = onComplete;
            lastClockSeconds = Time.unscaledTimeAsDouble;
            playing = autoPlay;
        }

        /// <summary>Seeks and resets this frame's clock; preserves the current Play/Pause state.</summary>
        public void SetFrame(int index)
        {
            RequireClip();
            if (index < 0 || index >= clip.frames.Length)
                throw new ArgumentOutOfRangeException(nameof(index), index,
                    "Buyu frame index is outside clip " + clip.id);
            RenderFrame(clip.frames[index]);
            frameIndex = index;
            elapsedInFrameMs = 0;
            completionSent = false;
            lastClockSeconds = Time.unscaledTimeAsDouble;
        }

        /// <summary>Resumes a paused clip; a completed single-shot clip starts again from frame zero.</summary>
        public void Play()
        {
            RequireClip();
            if (playing)
                return;
            if (completionSent)
                SetFrame(0);
            lastClockSeconds = Time.unscaledTimeAsDouble;
            playing = true;
        }

        public void Pause()
        {
            playing = false;
        }

        public void Replay()
        {
            SetFrame(0);
            Play();
        }

        private void Update()
        {
            if (!playing || clip == null)
                return;

            var now = Time.unscaledTimeAsDouble;
            var elapsedMs = Math.Max(0, now - lastClockSeconds) * 1000.0;
            lastClockSeconds = now;
            try
            {
                Advance(elapsedMs);
            }
            catch (Exception error)
            {
                playing = false;
                Debug.LogError("Buyu clip playback stopped at " + clip.id + ", frame " + frameIndex +
                    ". The resource or metadata error must be fixed; no placeholder frame was substituted.", this);
                Debug.LogException(error, this);
            }
        }

        private void Advance(double elapsedMs)
        {
            var looping = LoopOverride ?? clip.loop;
            elapsedInFrameMs += elapsedMs;
            // Whole loops have the same duration from every frame. Remove them before
            // advancing so a long editor stall cannot cause an unbounded catch-up loop.
            if (looping && elapsedInFrameMs >= cycleDurationMs)
                elapsedInFrameMs %= cycleDurationMs;

            var nextIndex = frameIndex;
            var completed = false;
            while (elapsedInFrameMs >= durationsMs[nextIndex])
            {
                elapsedInFrameMs -= durationsMs[nextIndex];
                if (nextIndex == clip.frames.Length - 1)
                {
                    if (looping)
                        nextIndex = 0;
                    else
                    {
                        completed = true;
                        elapsedInFrameMs = 0;
                        break;
                    }
                }
                else
                    nextIndex++;
            }

            if (nextIndex != frameIndex)
            {
                RenderFrame(clip.frames[nextIndex]);
                frameIndex = nextIndex;
            }

            if (completed)
            {
                playing = false;
                if (!completionSent)
                {
                    completionSent = true;
                    // Set all state before invoking a callback that may Replay or SetClip.
                    var callback = onComplete;
                    if (callback != null)
                        callback();
                }
            }
        }

        private void RenderFrame(ArtFrame frame)
        {
            if (target == null)
                target = GetComponent<Image>();
            if (target == null)
                throw new InvalidOperationException("BuyuClipPlayer needs a target Image: " + name);
            var rect = target.rectTransform;
            if (rect.anchorMin != rect.anchorMax)
                throw new InvalidOperationException(
                    "BuyuClipPlayer target needs fixed anchors so sizeDelta equals the declared display size: " +
                    target.name);

            var sprite = BuyuArtLoader.LoadSprite(frame);
            target.overrideSprite = null;
            target.sprite = sprite;
            target.type = Image.Type.Simple;
            target.preserveAspect = false;
            target.useSpriteMesh = false;
            target.color = Color.white;
            rect.pivot = new Vector2(frame.pivotX, 1f - frame.pivotY);
            rect.sizeDelta = new Vector2(frame.displayWidth, frame.displayHeight);
        }

        private void RequireClip()
        {
            if (clip == null || clip.frames == null || clip.frames.Length == 0)
                throw new InvalidOperationException("Set a valid Buyu clip before playback or seeking: " + name);
        }
    }
}
