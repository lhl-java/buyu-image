#if UNITY_EDITOR
using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

namespace Buyu.Editor
{
    public sealed class BuyuRuntimeAcceptance : MonoBehaviour
    {
        [Serializable] public class ClipResult
        {
            public string id; public bool loop; public int frames; public int observedFrames;
            public int callbacks; public bool wrapped; public bool playbackPassed;
            public double elapsedSeconds; public string renderedContact; public string error;
        }
        [Serializable] public class Result
        {
            public string generatedAt; public string unityVersion; public string status;
            public int width=1920,height=1080; public List<ClipResult> clips=new List<ClipResult>();
            public List<string> captures=new List<string>(); public List<string> errors=new List<string>();
            public int uiPointerChecks; public int captureEvents;
            public List<string> cannonMuzzleSamples=new List<string>();
            public bool actualPlayMode=true; public bool actualGraphicsRendered=false;
            public bool manualVisualApproval=false; public bool gameArtComplete=false;
        }
        private readonly Result result=new Result();
        private BuyuArtReview review;
        private Camera camera;
        private RenderTexture target;
        private string output;
        private IEnumerator routine;
        private void Start()
        {
            output=Path.GetFullPath(Path.Combine(Application.dataPath,Environment.GetCommandLineArgs().Contains("-buyuUiOnly")?"../Logs/RuntimeUiFinal":Environment.GetCommandLineArgs().Contains("-buyuSupplement")?"../Logs/RuntimeSupplement":"../Logs/RuntimeAcceptance"));
            Directory.CreateDirectory(output);
            result.generatedAt=DateTime.UtcNow.ToString("o"); result.unityVersion=Application.unityVersion;
            Application.logMessageReceived+=Logged;
            routine=Run();
        }
        private void Logged(string condition,string stack,LogType type)
        { if(type==LogType.Error || type==LogType.Exception || type==LogType.Assert) result.errors.Add(condition); }
        private void Update()
        {
            if(routine==null)return;
            try { if(!routine.MoveNext()) Finish(); }
            catch(Exception error) { result.errors.Add(error.ToString()); Finish(); }
        }
        private IEnumerator Run()
        {
            yield return null; yield return null;
            review=FindAnyObjectByType<BuyuArtReview>();
            if(review==null || review.AcceptanceError!=null)throw new Exception("Review startup failed: "+review?.AcceptanceError);
            var database=BuyuArtLoader.LoadDatabase();
            camera=Camera.main;
            target=new RenderTexture(1920,1080,24,RenderTextureFormat.ARGB32);
            target.Create(); camera.targetTexture=target;
            camera.aspect=1920f/1080f;
            foreach(var canvas in FindObjectsByType<Canvas>(FindObjectsSortMode.None))
                if(canvas.isRootCanvas) { canvas.renderMode=RenderMode.ScreenSpaceCamera;canvas.worldCamera=camera;canvas.planeDistance=10; }
            Canvas.ForceUpdateCanvases();
            yield return null;
            for(var n=0;n<database.clips.Length;n++)
            {
                var clip=database.clips[n];
                if(Environment.GetCommandLineArgs().Contains("-buyuUiOnly"))break;
                if(Environment.GetCommandLineArgs().Contains("-buyuSupplement") && !string.IsNullOrEmpty(clip.actorId) &&
                    !clip.actorId.StartsWith("34-") && !clip.actorId.StartsWith("35-") && !clip.actorId.StartsWith("36-"))continue;
                review.AcceptanceSelect("Motion",n,false);
                var player=review.AcceptancePlayer;
                var item=new ClipResult { id=clip.id,loop=clip.loop,frames=clip.frames.Length };
                result.clips.Add(item);
                var observed=new HashSet<int>(); var last=0; var cycles=0; var callbacks=0;
                // Preload all actual sprites before starting the real-time coverage clock.
                // Cold texture import/load stalls do not belong to an authored frame duration.
                foreach(var frame in clip.frames)BuyuArtLoader.LoadSprite(frame);
                yield return null; yield return null;
                player.LoopOverride=null;
                player.SetClip(clip,true,()=>callbacks++);
                var began=Time.unscaledTimeAsDouble;
                var duration=clip.frames.Sum(f=>f.durationMs>0?f.durationMs:1000/clip.fps)/1000.0;
                while(Time.unscaledTimeAsDouble-began<duration*(clip.loop?2.3:1.4)+.25)
                {
                    observed.Add(player.FrameIndex);
                    if(player.FrameIndex<last)cycles++;
                    last=player.FrameIndex;
                    yield return null;
                }
                item.elapsedSeconds=Time.unscaledTimeAsDouble-began;
                item.callbacks=callbacks;item.wrapped=cycles>0;item.observedFrames=observed.Count;
                item.playbackPassed=observed.Count==clip.frames.Length && (clip.loop?player.Playing&&cycles>0&&callbacks==0:!player.Playing&&callbacks==1&&player.FrameIndex==clip.frames.Length-1);
                if(!item.playbackPassed) {item.error="Real-time coverage or wrap/completion invariant failed.";result.errors.Add(clip.id+": "+item.error);}
                player.Pause();
                var rows=(clip.frames.Length+3)/4;
                var contact=new Texture2D(4*512,rows*384,TextureFormat.RGB24,false);
                for(var f=0;f<clip.frames.Length;f++)
                {
                    player.SetFrame(f);
                    Canvas.ForceUpdateCanvases();yield return null;
                    var rendered=ReadCamera();
                    // Fixed root-centred viewport for this clip, not a per-frame alpha fit.
                    var bounded=clip.frames.Where(x=>x.alphaBounds!=null&&x.alphaBounds.Length==4).ToArray();
                    var local=Vector2.zero;
                    if(bounded.Length>0)
                    {
                        var x=(bounded.Min(v=>v.alphaBounds[0])+bounded.Max(v=>v.alphaBounds[2]))*.5f;
                        var y=(bounded.Min(v=>v.alphaBounds[1])+bounded.Max(v=>v.alphaBounds[3]))*.5f;
                        var frame=clip.frames[0];
                        local=new Vector2((x/frame.width-frame.pivotX)*frame.displayWidth,(frame.pivotY-y/frame.height)*frame.displayHeight);
                    }
                    var root=camera.WorldToScreenPoint(player.Target.rectTransform.TransformPoint(local));
                    var cx=Mathf.Clamp(Mathf.RoundToInt(root.x)-256,0,1920-512);
                    var cy=Mathf.Clamp(Mathf.RoundToInt(root.y)-192,0,1080-384);
                    contact.SetPixels((f%4)*512,(rows-1-f/4)*384,512,384,rendered.GetPixels(cx,cy,512,384));
                    if(f==0 && n==0)Save(rendered,"review-motion.png");
                    Destroy(rendered);
                }
                contact.Apply();item.renderedContact="motion/"+clip.id.Replace('/','-')+".jpg";
                var file=Path.Combine(output,item.renderedContact);Directory.CreateDirectory(Path.GetDirectoryName(file));File.WriteAllBytes(file,contact.EncodeToJPG(92));Destroy(contact);
            }
            for(var n=0;n<database.screens.Length;n++)
            {
                if(Environment.GetCommandLineArgs().Contains("-buyuUiOnly"))break;
                review.AcceptanceSelect("Screens",n);yield return null;
                Save(ReadCamera(),"screens/"+database.screens[n].id+".png",true);
            }
            for(var n=0;n<database.uiFamilies.Length;n++)
            {
                review.AcceptanceSelect("UiStates",n);yield return null;
                Save(ReadCamera(),"ui/"+database.uiFamilies[n].id+".png",true);
                var controls=FindObjectsByType<BuyuRegisteredControl>(FindObjectsSortMode.None).Where(c=>c.gameObject.activeInHierarchy).ToArray();
                foreach(var control in controls)
                {
                    if(!control.Interactable)continue;
                    var carrier=control.GetComponentsInChildren<Image>().First(i=>i.raycastTarget);
                    var eventData=new PointerEventData(EventSystem.current){position=RectTransformUtility.WorldToScreenPoint(camera,carrier.rectTransform.position),button=PointerEventData.InputButton.Left,pointerId=-1};
                    // carrier's top-left pivot requires its geometric centre as hit point.
                    eventData.position=RectTransformUtility.WorldToScreenPoint(camera,carrier.rectTransform.TransformPoint(carrier.rectTransform.rect.center));
                    var hits=new List<RaycastResult>(); EventSystem.current.RaycastAll(eventData,hits);
                    var hit=hits.FirstOrDefault(h=>h.gameObject==carrier.gameObject);
                    if(hit.gameObject==null)throw new Exception("Actual GraphicRaycaster missed registered hit carrier: "+control.FamilyId);
                    eventData.pointerPressRaycast=hit;eventData.pointerCurrentRaycast=hit;
                    ExecuteEvents.ExecuteHierarchy(carrier.gameObject,eventData,ExecuteEvents.pointerDownHandler);
                    if(control.RequestedState!="pressed")result.errors.Add("Pointer down failed: "+control.FamilyId);
                    ExecuteEvents.ExecuteHierarchy(carrier.gameObject,eventData,ExecuteEvents.pointerUpHandler);
                    ExecuteEvents.ExecuteHierarchy(carrier.gameObject,eventData,ExecuteEvents.pointerClickHandler);
                    result.uiPointerChecks++;
                }
            }
            for(var n=0;n<database.cannons.Length;n++)
            {
                review.AcceptanceSelect("Cannons",n);yield return null;
                Save(ReadCamera(),"cannons/"+database.cannons[n].id+".png",true);
                foreach(var angle in new[]{-60f,0f,60f})
                {
                    review.AcceptanceCannonAngle(angle);yield return null;
                    var mouth=camera.WorldToScreenPoint(review.AcceptanceMuzzleWorld);
                    if(float.IsNaN(mouth.x)||mouth.x<0||mouth.x>1920||mouth.y<0||mouth.y>1080)
                        result.errors.Add("Registered muzzle outside view: "+database.cannons[n].id);
                    result.cannonMuzzleSamples.Add(database.cannons[n].id+" angle="+angle+" screen="+mouth);
                    Save(ReadCamera(),"cannons/"+database.cannons[n].id+"-angle-"+angle+".png",true);
                }
            }
            review.AcceptanceSelect("Assets",0);yield return null;
            foreach(var id in new[]{"ui/runtime-panel/panel-runtime","ui/panels/list-row","ui/panels/tooltip-panel"})
            {
                var asset=database.assets.First(a=>a.id==id);
                var obj=new GameObject("Nine slice acceptance",typeof(RectTransform),typeof(CanvasRenderer),typeof(Image));
                obj.transform.SetParent(review.AcceptanceStage,false);
                var image=obj.GetComponent<Image>();image.sprite=BuyuArtLoader.LoadSprite(asset);image.type=Image.Type.Sliced;image.raycastTarget=false;
                var rect=image.rectTransform;rect.anchorMin=rect.anchorMax=new Vector2(.5f,.5f);
                foreach(var width in new[]{640,960,1200})
                {rect.sizeDelta=new Vector2(width,id.Contains("panel-runtime")?620:id.Contains("list-row")?120:260);yield return null;Save(ReadCamera(),"stretch/"+asset.id.Replace('/','-')+"-"+width+".png",true);}
                obj.SetActive(false);Destroy(obj);
            }
            review.AcceptanceSelect("Fishing",0);yield return null;
            Save(ReadCamera(),"fishing-before.png",true);
            review.AcceptanceFire();var end=Time.unscaledTime+3;
            while(Time.unscaledTime<end)yield return null;
            result.captureEvents=review.AcceptanceCaptures;
            if(result.captureEvents<1)result.errors.Add("Fishing demonstration did not complete a capture event.");
            Save(ReadCamera(),"fishing-after.png",true);
        }
        private Texture2D ReadCamera()
        {
            Canvas.ForceUpdateCanvases();camera.Render();
            result.actualGraphicsRendered=true;
            var old=RenderTexture.active;RenderTexture.active=target;
            var texture=new Texture2D(1920,1080,TextureFormat.RGB24,false);
            texture.ReadPixels(new Rect(0,0,1920,1080),0,0);texture.Apply();RenderTexture.active=old;
            return texture;
        }
        private void Save(Texture2D texture,string name,bool destroy=false)
        {
            var file=Path.Combine(output,name);Directory.CreateDirectory(Path.GetDirectoryName(file));File.WriteAllBytes(file,texture.EncodeToPNG());result.captures.Add(name);
            if(destroy)Destroy(texture);
        }
        private void Finish()
        {
            routine=null;Application.logMessageReceived-=Logged;
            result.status=result.errors.Count==0?"runtime_technical_passed_visual_review_pending":"runtime_failed";
            File.WriteAllText(Path.Combine(output,"report.json"),JsonUtility.ToJson(result,true));
            Debug.Log("Buyu actual Play mode acceptance finished: "+result.status+", "+result.errors.Count+" errors.");
            if(Application.isBatchMode)EditorApplication.Exit(result.errors.Count==0?0:1);
            else EditorApplication.ExitPlaymode();
        }
    }
}

#endif
