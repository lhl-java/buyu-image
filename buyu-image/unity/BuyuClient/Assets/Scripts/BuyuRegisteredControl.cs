using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

namespace Buyu
{
    /// <summary>
    /// Reuses registered native PNGs at one family scale. Only the transparent child
    /// hit carrier is raycastable; EventSystem events bubble from it to this holder.
    /// No state alpha bounds, glow bounds or individual fit operation changes geometry.
    /// </summary>
    [DisallowMultipleComponent]
    [RequireComponent(typeof(RectTransform))]
    public sealed class BuyuRegisteredControl : MonoBehaviour, IPointerDownHandler,
        IPointerUpHandler, IPointerClickHandler, IPointerEnterHandler, IPointerExitHandler,
        ISelectHandler, IDeselectHandler, ISubmitHandler
    {
        private readonly Dictionary<string, RegisteredState> states =
            new Dictionary<string, RegisteredState>(StringComparer.OrdinalIgnoreCase);
        private readonly HashSet<string> reportedFallbacks = new HashSet<string>(StringComparer.Ordinal);
        private RectTransform holder;
        private Image artwork;
        private Image hitCarrier;
        private RectTransform labelArea;
        private Text liveLabel;
        private ArtUiFamily family;
        private Action clicked;
        private bool initialized;
        private bool interactable = true;
        private bool selected;
        private bool focused;
        private bool pointerInside;
        private int? pressedPointer;
        private int? pendingClickPointer;
        private bool toggleValue;
        private float familyScale;
        private string baseState;

        public string FamilyId { get { return family == null ? null : family.id; } }
        public float SharedDisplayScale { get { return familyScale; } }
        public string RequestedState { get; private set; }
        public string RenderedState { get; private set; }
        public bool UsesFallback { get; private set; }

        public bool Interactable
        {
            get { return interactable; }
            set
            {
                if (interactable == value)
                    return;
                interactable = value;
                ClearPointerState();
                RefreshVisual();
            }
        }

        /// <summary>
        /// Persistent selection, or the on/off value for toggle and checkbox families.
        /// EventSystem focus is separate and never changes a toggle's stored value.
        /// A toggle click updates this value before invoking the supplied callback.
        /// </summary>
        public bool Selected
        {
            get { return selected; }
            set
            {
                if (selected == value)
                    return;
                selected = value;
                RefreshVisual();
            }
        }

        public void Init(ArtUiFamily value, Dictionary<string, ArtAsset> assets,
            Font font, string label, Action clicked)
        {
            if (value == null || string.IsNullOrWhiteSpace(value.id))
                throw new ArgumentException("A registered Buyu UI family and id are required.", nameof(value));
            if (assets == null)
                throw new ArgumentNullException(nameof(assets));
            ValidateSize(value.logicalCanvas, "logicalCanvas", value.id);
            ValidateRect(value.contentRect, value.logicalCanvas, "contentRect", value.id);
            ValidateRect(value.hitRect, value.logicalCanvas, "hitRect", value.id);
            if (!Finite(value.sharedDisplayScale) || value.sharedDisplayScale <= 0f ||
                value.sharedDisplayScale > 1f)
                throw new InvalidDataException("Buyu UI family needs one positive scale no greater than one: " + value.id);
            if (value.states == null || value.states.Length == 0)
                throw new InvalidDataException("Buyu UI family has no registered states: " + value.id);
            var usesToggleValue = value.id == "toggle" || value.id == "checkbox";
            var requiredBase = usesToggleValue ? "off" : "normal";
            var hasLabel = SupportsLabel(value.id) && !string.IsNullOrEmpty(label);
            if (hasLabel && font == null)
                throw new ArgumentNullException(nameof(font), "Live Chinese labels require the bundled imported Font.");

            // Validate and resolve original sprites before replacing an existing control.
            var prepared = new Dictionary<string, RegisteredState>(StringComparer.OrdinalIgnoreCase);
            foreach (var state in value.states)
            {
                if (state == null || string.IsNullOrWhiteSpace(state.state) || string.IsNullOrWhiteSpace(state.assetId))
                    throw new InvalidDataException("Buyu UI family contains an incomplete state: " + value.id);
                var key = state.state.Trim().ToLowerInvariant();
                if (prepared.ContainsKey(key))
                    throw new InvalidDataException("Duplicate Buyu UI state: " + value.id + "/" + key);
                ArtAsset asset;
                if (!assets.TryGetValue(state.assetId, out asset) || asset == null)
                    throw new FileNotFoundException("Missing registered Buyu UI asset: " + state.assetId);
                BuyuArtLoader.ValidateFrame(asset);
                if (state.drawOffset == null || state.drawOffset.Length != 2 ||
                    !Finite(state.drawOffset[0]) || !Finite(state.drawOffset[1]) ||
                    state.drawOffset[0] < 0f || state.drawOffset[1] < 0f ||
                    state.drawOffset[0] + asset.width > value.logicalCanvas[0] + .01f ||
                    state.drawOffset[1] + asset.height > value.logicalCanvas[1] + .01f)
                    throw new InvalidDataException("Registered PNG does not fit its logical canvas without cropping: " +
                        value.id + "/" + key);
                prepared.Add(key, new RegisteredState(asset, BuyuArtLoader.LoadSprite(asset),
                    new Vector2(state.drawOffset[0], state.drawOffset[1])));
            }
            if (!prepared.ContainsKey(requiredBase))
                throw new InvalidDataException("Buyu UI family lacks its explicit fallback state " + requiredBase + ": " + value.id);

            holder = GetComponent<RectTransform>();
            if (holder == null)
                throw new InvalidOperationException("BuyuRegisteredControl needs a RectTransform holder.");
            if (holder.anchorMin != holder.anchorMax)
                throw new InvalidOperationException(
                    "BuyuRegisteredControl needs fixed holder anchors so its logical canvas size stays exact: " + value.id);
            EnsureChildren();
            family = value;
            familyScale = value.sharedDisplayScale;
            toggleValue = usesToggleValue;
            baseState = requiredBase;
            this.clicked = clicked;
            states.Clear();
            foreach (var pair in prepared)
                states.Add(pair.Key, pair.Value);
            reportedFallbacks.Clear();
            focused = false;
            ClearPointerState();
            holder.sizeDelta = new Vector2(value.logicalCanvas[0], value.logicalCanvas[1]) * familyScale;
            PlaceRect(hitCarrier.rectTransform, value.hitRect);
            PlaceRect(labelArea, value.contentRect);
            liveLabel.font = font;
            liveLabel.fontStyle = FontStyle.Normal;
            // Typography tokens are already logical display pixels. Never shrink the
            // label to a particular state's bounds; long labels clip in the fixed content area.
            liveLabel.fontSize = value.id == "primary" ? 28 : value.id == "secondary" ? 26 : 24;
            liveLabel.text = hasLabel ? label : string.Empty;
            labelArea.gameObject.SetActive(hasLabel);
            initialized = true;
            RefreshVisual();
        }

        public void OnPointerDown(PointerEventData eventData)
        {
            if (!ReadyForPointer(eventData) || !ContainsPointer(eventData) ||
                (pressedPointer.HasValue && pressedPointer.Value != eventData.pointerId))
                return;
            pressedPointer = eventData.pointerId;
            pendingClickPointer = null;
            pointerInside = true;
            if (EventSystem.current != null)
                EventSystem.current.SetSelectedGameObject(gameObject, eventData);
            RefreshVisual();
        }

        public void OnPointerUp(PointerEventData eventData)
        {
            if (eventData == null || !pressedPointer.HasValue || pressedPointer.Value != eventData.pointerId)
                return;
            pendingClickPointer = ReadyForPointer(eventData) && ContainsPointer(eventData)
                ? (int?)eventData.pointerId : null;
            pressedPointer = null;
            pointerInside = ContainsPointer(eventData);
            RefreshVisual();
        }

        public void OnPointerClick(PointerEventData eventData)
        {
            var accepted = ReadyForPointer(eventData) && pendingClickPointer.HasValue &&
                pendingClickPointer.Value == eventData.pointerId && ContainsPointer(eventData);
            pendingClickPointer = null;
            if (accepted)
                Activate();
        }

        public void OnPointerEnter(PointerEventData eventData)
        {
            if (eventData == null || (pressedPointer.HasValue && pressedPointer.Value != eventData.pointerId))
                return;
            pointerInside = ContainsPointer(eventData);
            RefreshVisual();
        }

        public void OnPointerExit(PointerEventData eventData)
        {
            if (eventData == null || (pressedPointer.HasValue && pressedPointer.Value != eventData.pointerId))
                return;
            pointerInside = false;
            RefreshVisual();
        }

        public void OnSelect(BaseEventData eventData)
        {
            focused = true;
            RefreshVisual();
        }

        public void OnDeselect(BaseEventData eventData)
        {
            focused = false;
            ClearPointerState();
            RefreshVisual();
        }

        public void OnSubmit(BaseEventData eventData)
        {
            if (initialized && interactable && isActiveAndEnabled)
                Activate();
        }

        private void OnEnable()
        {
            RefreshVisual();
        }

        private void OnDisable()
        {
            focused = false;
            ClearPointerState();
        }

        private void Activate()
        {
            if (toggleValue)
                selected = !selected;
            RefreshVisual();
            var callback = clicked;
            if (callback != null)
                callback();
        }

        private void RefreshVisual()
        {
            if (!initialized)
                return;
            var semantic = toggleValue ? (selected ? "on" : "off") :
                (selected || focused ? "selected" : "normal");
            RequestedState = !interactable ? "disabled" :
                pressedPointer.HasValue && pointerInside ? "pressed" : semantic;
            RegisteredState state;
            var actual = RequestedState;
            if (!states.TryGetValue(actual, out state))
            {
                // Preserve an existing on/selected semantic state while an unavailable
                // pressed/disabled state uses client tint. Otherwise use normal/off.
                actual = (RequestedState == "pressed" || RequestedState == "disabled") && states.ContainsKey(semantic)
                    ? semantic : baseState;
                state = states[actual];
                var fallbackKey = RequestedState + "->" + actual;
                if (reportedFallbacks.Add(fallbackKey))
                    Debug.LogWarning("Buyu UI " + family.id + " has no original " + RequestedState +
                        " PNG; explicitly reusing " + actual +
                        " at the same registered scale. This fallback is not a separately drawn state.", this);
            }
            RenderedState = actual;
            UsesFallback = actual != RequestedState;
            artwork.sprite = state.sprite;
            artwork.color = UsesFallback && RequestedState == "disabled"
                ? new Color(.7f, .7f, .7f, .72f)
                : UsesFallback && RequestedState == "pressed" ? new Color(.90f, .90f, .90f, 1f) : Color.white;
            var artRect = artwork.rectTransform;
            artRect.anchoredPosition = new Vector2(state.offset.x, -state.offset.y) * familyScale;
            artRect.sizeDelta = new Vector2(state.asset.width, state.asset.height) * familyScale;
            var lightText = family.id == "primary" || (family.id == "tab" && actual == "selected");
            var textColor = lightText ? new Color(1f, 244f / 255f, 214f / 255f) :
                new Color(24f / 255f, 63f / 255f, 54f / 255f);
            if (!interactable)
                textColor = lightText ? new Color(textColor.r, textColor.g, textColor.b, .72f) :
                    new Color(133f / 255f, 129f / 255f, 118f / 255f);
            liveLabel.color = textColor;
        }

        private void EnsureChildren()
        {
            if (artwork == null)
            {
                artwork = NewChild("Registered native artwork").gameObject.AddComponent<Image>();
                artwork.raycastTarget = false;
                artwork.type = Image.Type.Simple;
                artwork.preserveAspect = false;
                artwork.useSpriteMesh = false;
            }
            if (labelArea == null)
            {
                labelArea = NewChild("Registered text content area");
                labelArea.gameObject.AddComponent<RectMask2D>();
                var textRect = NewChild("Live regular label", labelArea);
                textRect.anchorMin = Vector2.zero;
                textRect.anchorMax = Vector2.one;
                textRect.offsetMin = textRect.offsetMax = Vector2.zero;
                liveLabel = textRect.gameObject.AddComponent<Text>();
                liveLabel.raycastTarget = false;
                liveLabel.alignment = TextAnchor.MiddleCenter;
                liveLabel.fontStyle = FontStyle.Normal;
                liveLabel.supportRichText = false;
                liveLabel.resizeTextForBestFit = false;
                liveLabel.horizontalOverflow = HorizontalWrapMode.Overflow;
                liveLabel.verticalOverflow = VerticalWrapMode.Truncate;
                liveLabel.lineSpacing = 1f;
            }
            if (hitCarrier == null)
            {
                hitCarrier = NewChild("Registered hit area").gameObject.AddComponent<Image>();
                hitCarrier.sprite = null;
                hitCarrier.color = new Color(1f, 1f, 1f, 0f);
                hitCarrier.raycastTarget = true;
                hitCarrier.alphaHitTestMinimumThreshold = 0f;
                // Keep an alpha-zero raycast carrier from being culled as transparent geometry.
                hitCarrier.canvasRenderer.cullTransparentMesh = false;
            }
        }

        private RectTransform NewChild(string childName, RectTransform parent = null)
        {
            var child = new GameObject(childName, typeof(RectTransform));
            child.transform.SetParent(parent == null ? holder : parent, false);
            var rect = child.GetComponent<RectTransform>();
            rect.anchorMin = rect.anchorMax = new Vector2(0f, 1f);
            rect.pivot = new Vector2(0f, 1f);
            return rect;
        }

        private void PlaceRect(RectTransform rect, float[] data)
        {
            rect.anchoredPosition = new Vector2(data[0], -data[1]) * familyScale;
            rect.sizeDelta = new Vector2(data[2], data[3]) * familyScale;
        }

        private bool ReadyForPointer(PointerEventData eventData)
        {
            return initialized && interactable && isActiveAndEnabled && eventData != null &&
                   eventData.button == PointerEventData.InputButton.Left;
        }

        private bool ContainsPointer(PointerEventData eventData)
        {
            return hitCarrier != null && eventData != null &&
                RectTransformUtility.RectangleContainsScreenPoint(hitCarrier.rectTransform, eventData.position,
                    eventData.pressEventCamera != null ? eventData.pressEventCamera : eventData.enterEventCamera);
        }

        private void ClearPointerState()
        {
            pressedPointer = null;
            pendingClickPointer = null;
            pointerInside = false;
        }

        private static bool SupportsLabel(string id)
        {
            return id == "primary" || id == "secondary" || id == "tab";
        }

        private static void ValidateSize(float[] value, string field, string id)
        {
            if (value == null || value.Length != 2 || !Finite(value[0]) || !Finite(value[1]) ||
                value[0] <= 0f || value[1] <= 0f)
                throw new InvalidDataException("Buyu UI " + id + " needs a positive two-value " + field + ".");
        }

        private static void ValidateRect(float[] value, float[] canvas, string field, string id)
        {
            if (value == null || value.Length != 4 || !Finite(value[0]) || !Finite(value[1]) ||
                !Finite(value[2]) || !Finite(value[3]) || value[0] < 0f || value[1] < 0f ||
                value[2] <= 0f || value[3] <= 0f || value[0] + value[2] > canvas[0] + .01f ||
                value[1] + value[3] > canvas[1] + .01f)
                throw new InvalidDataException("Buyu UI " + id + " has invalid top-left x,y,width,height " + field + ".");
        }

        private static bool Finite(float value)
        {
            return !float.IsNaN(value) && !float.IsInfinity(value);
        }

        private sealed class RegisteredState
        {
            public readonly ArtAsset asset;
            public readonly Sprite sprite;
            public readonly Vector2 offset;

            public RegisteredState(ArtAsset asset, Sprite sprite, Vector2 offset)
            {
                this.asset = asset;
                this.sprite = sprite;
                this.offset = offset;
            }
        }
    }
}
