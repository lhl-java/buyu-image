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
    [InitializeOnLoad]
    public static class BuyuRuntimeAcceptanceEntry
    {
        static BuyuRuntimeAcceptanceEntry() { EditorApplication.playModeStateChanged += Changed; }
        public static void Run()
        {
            BuyuProjectBootstrap.CreateOrOpenArtReviewScene();
            if (!File.Exists(BuyuProjectBootstrap.ScenePath))
                throw new InvalidOperationException("Art review scene creation failed; do not run an empty scene.");
            SessionState.SetBool("Buyu.Acceptance.Pending", true);
            EditorApplication.EnterPlaymode();
        }
        private static void Changed(PlayModeStateChange state)
        {
            if (state != PlayModeStateChange.EnteredPlayMode || !SessionState.GetBool("Buyu.Acceptance.Pending", false)) return;
            SessionState.SetBool("Buyu.Acceptance.Pending", false);
            new GameObject("Actual runtime acceptance").AddComponent<BuyuRuntimeAcceptance>();
        }
    }

}
