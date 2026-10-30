using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Buyu.Editor
{
    /// <summary>Creates the review scene once; existing scenes are never rebuilt.</summary>
    [InitializeOnLoad]
    public static class BuyuProjectBootstrap
    {
        public const string ScenePath = "Assets/Scenes/BuyuArtReview.unity";
        private const string MenuPath = "Buyu/Create or Open Art Review Scene";

        static BuyuProjectBootstrap()
        {
            EditorApplication.delayCall += CreateMissingSceneAfterImport;
        }

        private static void CreateMissingSceneAfterImport()
        {
            if (EditorApplication.isPlayingOrWillChangePlaymode || Application.isBatchMode)
                return;

            if (EditorApplication.isCompiling || EditorApplication.isUpdating)
            {
                EditorApplication.delayCall += CreateMissingSceneAfterImport;
                return;
            }

            if (File.Exists(ScenePath))
                return;

            try
            {
                CreateSceneAssetIfMissing();
                Debug.Log("Buyu art review scene created. Open it with " + MenuPath + ".");
            }
            catch (Exception error)
            {
                // A failed import remains visible; do not retry repeatedly or replace a scene.
                Debug.LogException(error);
            }
        }

        [MenuItem(MenuPath)]
        public static void CreateOrOpenArtReviewScene()
        {
            if (EditorApplication.isPlayingOrWillChangePlaymode)
                return;

            try
            {
                CreateSceneAssetIfMissing();
                EnsureBuildScene();

                var loadedScene = SceneManager.GetSceneByPath(ScenePath);
                if (loadedScene.IsValid() && loadedScene.isLoaded)
                {
                    SceneManager.SetActiveScene(loadedScene);
                    return;
                }

                // Opening another scene must preserve the user's unsaved work.
                if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())
                    return;

                EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            }
            catch (Exception error)
            {
                Debug.LogException(error);
            }
        }

        [MenuItem(MenuPath, true)]
        private static bool CanOpenArtReviewScene()
        {
            return !EditorApplication.isCompiling && !EditorApplication.isUpdating &&
                   !EditorApplication.isPlayingOrWillChangePlaymode;
        }

        private static void CreateSceneAssetIfMissing()
        {
            if (File.Exists(ScenePath))
                return;

            if (!AssetDatabase.IsValidFolder("Assets/Scenes"))
                AssetDatabase.CreateFolder("Assets", "Scenes");

            var previousScene = SceneManager.GetActiveScene();
            // A fresh batch editor has an unsaved untitled scene and rejects additive creation.
            // Only this batch startup path can replace that empty scene without an editor prompt.
            var batchUntitled = Application.isBatchMode && string.IsNullOrEmpty(previousScene.path);
            var reviewScene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,
                batchUntitled ? NewSceneMode.Single : NewSceneMode.Additive);
            try
            {
                var cameraObject = new GameObject("Main Camera");
                SceneManager.MoveGameObjectToScene(cameraObject, reviewScene);
                cameraObject.tag = "MainCamera";
                cameraObject.transform.position = new Vector3(0, 0, -10);
                var camera = cameraObject.AddComponent<Camera>();
                camera.orthographic = true;
                camera.orthographicSize = 5;
                camera.clearFlags = CameraClearFlags.SolidColor;
                camera.backgroundColor = new Color(0.05f, 0.12f, 0.14f, 1);

                var reviewObject = new GameObject("Buyu Art Review");
                SceneManager.MoveGameObjectToScene(reviewObject, reviewScene);
                reviewObject.AddComponent<BuyuArtReview>();

                if (!EditorSceneManager.SaveScene(reviewScene, ScenePath))
                    throw new IOException("Could not save " + ScenePath);

                ApplyReviewProjectDefaults();
                EnsureBuildScene();
            }
            finally
            {
                if (previousScene.IsValid() && previousScene.isLoaded)
                    SceneManager.SetActiveScene(previousScene);
                if (!batchUntitled && reviewScene.IsValid() && reviewScene.isLoaded)
                    EditorSceneManager.CloseScene(reviewScene, true);
            }
        }

        private static void ApplyReviewProjectDefaults()
        {
            var brand = BuyuArtLoader.LoadDatabase();
            if (!string.IsNullOrWhiteSpace(brand.gameName))
                PlayerSettings.productName = brand.gameName;
            EditorSettings.defaultBehaviorMode = EditorBehaviorMode.Mode2D;
            PlayerSettings.defaultScreenWidth = 1920;
            PlayerSettings.defaultScreenHeight = 1080;
            PlayerSettings.fullScreenMode = FullScreenMode.Windowed;
        }

        private static void EnsureBuildScene()
        {
            var scenes = new List<EditorBuildSettingsScene>(EditorBuildSettings.scenes);
            var index = scenes.FindIndex(scene => scene.path == ScenePath);
            if (index < 0)
            {
                scenes.Insert(0, new EditorBuildSettingsScene(ScenePath, true));
                EditorBuildSettings.scenes = scenes.ToArray();
            }
            else if (!scenes[index].enabled)
            {
                scenes[index] = new EditorBuildSettingsScene(ScenePath, true);
                EditorBuildSettings.scenes = scenes.ToArray();
            }
        }
    }
}
