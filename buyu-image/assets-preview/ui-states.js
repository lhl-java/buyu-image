window.BUYU_UI_STATES = {
  "schemaVersion": 1,
  "generatedAt": "2026-10-28T10:47:39.763477+00:00",
  "status": "accepted_Unity_shared_registration",
  "coordinateSystem": {
    "units": "native source pixels",
    "rectFormat": "x,y,width,height",
    "origin": "top-left",
    "drawOffset": "source PNG top-left inside shared logical canvas",
    "integerPlacement": true,
    "maxCoreCenterRoundingErrorPx": 0.5
  },
  "operation": {
    "type": "read_native_alpha_write_metadata",
    "pngWrites": 0,
    "sourceResize": false,
    "sourcePixelsModified": false,
    "renderedPreviews": 0,
    "atlasRebuild": false
  },
  "inputs": [
    "assets/ui/buttons/manifest.json",
    "assets/ui/hud/manifest.json",
    "assets/ui/additions/manifest.json",
    "designs/production-v1/kit-buttons/kit-buttons.visual-qa.json",
    "designs/production-v1/kit-hud/kit-hud.visual-qa.json"
  ],
  "coreHeuristic": {
    "alphaThreshold": 224,
    "avoidThreshold254": true,
    "reason": "Near-opaque texture is not uniformly alpha255; selected slot maxAlpha254 has sparse alpha254 coverage. Exact max-alpha bbox is not a reliable body silhouette."
  },
  "families": [
    {
      "id": "primary",
      "status": "accepted_Unity_shared_registration",
      "referenceState": "normal",
      "logicalCanvas": [
        382,
        180
      ],
      "logicalRoot": [
        191,
        90
      ],
      "logicalAnchor": [
        0.5,
        0.5
      ],
      "referenceBodyRect": [
        27,
        31,
        329,
        118
      ],
      "contentRect": [
        85,
        51,
        213,
        78
      ],
      "contentRectRole": "candidate live-text safe area",
      "hitRect": [
        27,
        31,
        329,
        118
      ],
      "hitShape": "rounded_rect",
      "preferredBodyDisplayBox": [
        280,
        100
      ],
      "sharedDisplayScale": 0.8474576,
      "displayCanvasSize": [
        323.729,
        152.542
      ],
      "scaleRule": "Compute one family scale from the reference body and use it unchanged for all states. Never fit each source/glow bbox separately.",
      "futurePaddingExport": {
        "allowed": true,
        "canvas": [
          382,
          180
        ],
        "placement": "state.drawOffset",
        "resample": false,
        "upscale": false,
        "note": "Future optional RGBA padding only. No padded PNG is produced by this metadata tool."
      },
      "stateFallbacks": {
        "hover": "reuse current semantic state; client color feedback only; no geometry change",
        "focus": "client focus indicator outside contentRect; no artwork rescale"
      },
      "states": [
        {
          "state": "normal",
          "assetId": "ui/buttons/primary-normal",
          "file": "assets/ui/buttons/primary-normal.png",
          "generationRecord": "assets/ui/buttons/primary-normal.png.generation.json",
          "sourceSha256FromManifest": "421410e59b3a8773c3bec36c1f7f468a82e5fc9d20c0a783dbb659f4614e7f45",
          "sourceNativeSize": [
            344,
            133
          ],
          "candidateCoreRect": [
            8,
            9,
            329,
            118
          ],
          "coreCenter": [
            172.5,
            68.0
          ],
          "coreMeasurement": {
            "method": "alpha_threshold_bbox",
            "threshold": 224,
            "thresholdIsArtHeuristic": true,
            "maxAlpha": 255,
            "boundsLTRBByAlpha": {
              "192": [
                8,
                8,
                337,
                128
              ],
              "224": [
                8,
                9,
                337,
                127
              ],
              "240": [
                9,
                9,
                336,
                127
              ]
            },
            "opticalSilhouetteApproved": false
          },
          "status": "accepted_Unity_art",
          "drawOffset": [
            19,
            22
          ],
          "drawScale": 1,
          "drawRect": [
            19,
            22,
            344,
            133
          ],
          "registeredCoreCenter": [
            191.5,
            90.0
          ],
          "rootResidualPx": [
            0.5,
            0.0
          ],
          "coreExtentDriftFromReference": [
            0.0,
            0.0
          ]
        },
        {
          "state": "pressed",
          "assetId": "ui/buttons/primary-pressed",
          "file": "assets/ui/buttons/primary-pressed.png",
          "generationRecord": "assets/ui/buttons/primary-pressed.png.generation.json",
          "sourceSha256FromManifest": "b5543b36ceb21aac090032ad8bc9f7d8d7511d2e4fe014de18da2c858a014963",
          "sourceNativeSize": [
            344,
            132
          ],
          "candidateCoreRect": [
            8,
            8,
            329,
            118
          ],
          "coreCenter": [
            172.5,
            67.0
          ],
          "coreMeasurement": {
            "method": "alpha_threshold_bbox",
            "threshold": 224,
            "thresholdIsArtHeuristic": true,
            "maxAlpha": 255,
            "boundsLTRBByAlpha": {
              "192": [
                7,
                7,
                337,
                127
              ],
              "224": [
                8,
                8,
                337,
                126
              ],
              "240": [
                8,
                8,
                336,
                126
              ]
            },
            "opticalSilhouetteApproved": false
          },
          "status": "accepted_Unity_art",
          "drawOffset": [
            19,
            23
          ],
          "drawScale": 1,
          "drawRect": [
            19,
            23,
            344,
            132
          ],
          "registeredCoreCenter": [
            191.5,
            90.0
          ],
          "rootResidualPx": [
            0.5,
            0.0
          ],
          "coreExtentDriftFromReference": [
            0.0,
            0.0
          ]
        },
        {
          "state": "disabled",
          "assetId": "ui/buttons/primary-disabled",
          "file": "assets/ui/buttons/primary-disabled.png",
          "generationRecord": "assets/ui/buttons/primary-disabled.png.generation.json",
          "sourceSha256FromManifest": "23625154ed59351cd856f1491c0f3630b3fd2fc2e413601c5b50e50749726058",
          "sourceNativeSize": [
            345,
            133
          ],
          "candidateCoreRect": [
            7,
            8,
            330,
            119
          ],
          "coreCenter": [
            172.0,
            67.5
          ],
          "coreMeasurement": {
            "method": "alpha_threshold_bbox",
            "threshold": 224,
            "thresholdIsArtHeuristic": true,
            "maxAlpha": 255,
            "boundsLTRBByAlpha": {
              "192": [
                7,
                8,
                337,
                128
              ],
              "224": [
                7,
                8,
                337,
                127
              ],
              "240": [
                8,
                8,
                337,
                127
              ]
            },
            "opticalSilhouetteApproved": false
          },
          "status": "accepted_Unity_art",
          "drawOffset": [
            19,
            23
          ],
          "drawScale": 1,
          "drawRect": [
            19,
            23,
            345,
            133
          ],
          "registeredCoreCenter": [
            191.0,
            90.5
          ],
          "rootResidualPx": [
            0.0,
            0.5
          ],
          "coreExtentDriftFromReference": [
            0.00304,
            0.00847
          ]
        },
        {
          "state": "selected",
          "assetId": "ui/buttons/primary-selected",
          "file": "assets/ui/buttons/primary-selected.png",
          "generationRecord": "assets/ui/buttons/primary-selected.png.generation.json",
          "sourceSha256FromManifest": "9e640e22035d7012d22f19e27453176608b8a20ba2111e03d5ec7b55295e7dfe",
          "sourceNativeSize": [
            364,
            162
          ],
          "candidateCoreRect": [
            15,
            18,
            332,
            124
          ],
          "coreCenter": [
            181.0,
            80.0
          ],
          "coreMeasurement": {
            "method": "alpha_threshold_bbox",
            "threshold": 224,
            "thresholdIsArtHeuristic": true,
            "maxAlpha": 255,
            "boundsLTRBByAlpha": {
              "192": [
                15,
                18,
                348,
                142
              ],
              "224": [
                15,
                18,
                347,
                142
              ],
              "240": [
                16,
                19,
                347,
                142
              ]
            },
            "opticalSilhouetteApproved": false
          },
          "status": "accepted_Unity_art",
          "drawOffset": [
            10,
            10
          ],
          "drawScale": 1,
          "drawRect": [
            10,
            10,
            364,
            162
          ],
          "registeredCoreCenter": [
            191.0,
            90.0
          ],
          "rootResidualPx": [
            0.0,
            0.0
          ],
          "coreExtentDriftFromReference": [
            0.00912,
            0.05085
          ]
        }
      ]
    },
    {
      "id": "secondary",
      "status": "accepted_Unity_shared_registration",
      "referenceState": "normal",
      "logicalCanvas": [
        382,
        180
      ],
      "logicalRoot": [
        191,
        90
      ],
      "logicalAnchor": [
        0.5,
        0.5
      ],
      "referenceBodyRect": [
        29,
        31,
        325,
        118
      ],
      "contentRect": [
        87,
        51,
        209,
        78
      ],
      "contentRectRole": "candidate live-text safe area",
      "hitRect": [
        29,
        31,
        325,
        118
      ],
      "hitShape": "rounded_rect",
      "preferredBodyDisplayBox": [
        248,
        88
      ],
      "sharedDisplayScale": 0.7457627,
      "displayCanvasSize": [
        284.881,
        134.237
      ],
      "scaleRule": "Compute one family scale from the reference body and use it unchanged for all states. Never fit each source/glow bbox separately.",
      "futurePaddingExport": {
        "allowed": true,
        "canvas": [
          382,
          180
        ],
        "placement": "state.drawOffset",
        "resample": false,
        "upscale": false,
        "note": "Future optional RGBA padding only. No padded PNG is produced by this metadata tool."
      },
      "stateFallbacks": {
        "hover": "reuse current semantic state; client color feedback only; no geometry change",
        "focus": "client focus indicator outside contentRect; no artwork rescale"
      },
      "states": [
        {
          "state": "normal",
          "assetId": "ui/buttons/secondary-normal",
          "file": "assets/ui/buttons/secondary-normal.png",
          "generationRecord": "assets/ui/buttons/secondary-normal.png.generation.json",
          "sourceSha256FromManifest": "46d45bec5225aff71df93b769b89d429bb5b60cb63f0a6104db36afc468f9614",
          "sourceNativeSize": [
            339,
            136
          ],
          "candidateCoreRect": [
            8,
            8,
            325,
            118
          ],
          "coreCenter": [
            170.5,
            67.0
          ],
          "coreMeasurement": {
            "method": "alpha_threshold_bbox",
            "threshold": 224,
            "thresholdIsArtHeuristic": true,
            "maxAlpha": 255,
            "boundsLTRBByAlpha": {
              "192": [
                7,
                8,
                334,
                126
              ],
              "224": [
                8,
                8,
                333,
                126
              ],
              "240": [
                8,
                8,
                333,
                125
              ]
            },
            "opticalSilhouetteApproved": false
          },
          "status": "accepted_Unity_art",
          "drawOffset": [
            21,
            23
          ],
          "drawScale": 1,
          "drawRect": [
            21,
            23,
            339,
            136
          ],
          "registeredCoreCenter": [
            191.5,
            90.0
          ],
          "rootResidualPx": [
            0.5,
            0.0
          ],
          "coreExtentDriftFromReference": [
            0.0,
            0.0
          ]
        },
        {
          "state": "pressed",
          "assetId": "ui/buttons/secondary-pressed",
          "file": "assets/ui/buttons/secondary-pressed.png",
          "generationRecord": "assets/ui/buttons/secondary-pressed.png.generation.json",
          "sourceSha256FromManifest": "9b0bd71160c2d46632beb1f01cff58db3391251ab65d34385569d664b8f9c238",
          "sourceNativeSize": [
            341,
            137
          ],
          "candidateCoreRect": [
            8,
            8,
            326,
            118
          ],
          "coreCenter": [
            171.0,
            67.0
          ],
          "coreMeasurement": {
            "method": "alpha_threshold_bbox",
            "threshold": 224,
            "thresholdIsArtHeuristic": true,
            "maxAlpha": 255,
            "boundsLTRBByAlpha": {
              "192": [
                7,
                8,
                335,
                126
              ],
              "224": [
                8,
                8,
                334,
                126
              ],
              "240": [
                9,
                8,
                334,
                125
              ]
            },
            "opticalSilhouetteApproved": false
          },
          "status": "accepted_Unity_art",
          "drawOffset": [
            20,
            23
          ],
          "drawScale": 1,
          "drawRect": [
            20,
            23,
            341,
            137
          ],
          "registeredCoreCenter": [
            191.0,
            90.0
          ],
          "rootResidualPx": [
            0.0,
            0.0
          ],
          "coreExtentDriftFromReference": [
            0.00308,
            0.0
          ]
        },
        {
          "state": "disabled",
          "assetId": "ui/buttons/secondary-disabled",
          "file": "assets/ui/buttons/secondary-disabled.png",
          "generationRecord": "assets/ui/buttons/secondary-disabled.png.generation.json",
          "sourceSha256FromManifest": "bda8a266fee8bc4fc511d9239a99a8553a1aa9042de960696595394ffc92f023",
          "sourceNativeSize": [
            344,
            137
          ],
          "candidateCoreRect": [
            7,
            8,
            330,
            119
          ],
          "coreCenter": [
            172.0,
            67.5
          ],
          "coreMeasurement": {
            "method": "alpha_threshold_bbox",
            "threshold": 224,
            "thresholdIsArtHeuristic": true,
            "maxAlpha": 255,
            "boundsLTRBByAlpha": {
              "192": [
                7,
                8,
                337,
                127
              ],
              "224": [
                7,
                8,
                337,
                127
              ],
              "240": [
                8,
                8,
                337,
                126
              ]
            },
            "opticalSilhouetteApproved": false
          },
          "status": "accepted_Unity_art",
          "drawOffset": [
            19,
            23
          ],
          "drawScale": 1,
          "drawRect": [
            19,
            23,
            344,
            137
          ],
          "registeredCoreCenter": [
            191.0,
            90.5
          ],
          "rootResidualPx": [
            0.0,
            0.5
          ],
          "coreExtentDriftFromReference": [
            0.01538,
            0.00847
          ]
        },
        {
          "state": "selected",
          "assetId": "ui/buttons/secondary-selected",
          "file": "assets/ui/buttons/secondary-selected.png",
          "generationRecord": "assets/ui/buttons/secondary-selected.png.generation.json",
          "sourceSha256FromManifest": "80cc7126aa694a32adf7bd5a1df8f10669b40a8879b15231216339308f73ba5b",
          "sourceNativeSize": [
            363,
            161
          ],
          "candidateCoreRect": [
            15,
            20,
            331,
            123
          ],
          "coreCenter": [
            180.5,
            81.5
          ],
          "coreMeasurement": {
            "method": "alpha_threshold_bbox",
            "threshold": 224,
            "thresholdIsArtHeuristic": true,
            "maxAlpha": 255,
            "boundsLTRBByAlpha": {
              "192": [
                15,
                20,
                346,
                143
              ],
              "224": [
                15,
                20,
                346,
                143
              ],
              "240": [
                16,
                21,
                345,
                142
              ]
            },
            "opticalSilhouetteApproved": false
          },
          "status": "accepted_Unity_art",
          "drawOffset": [
            11,
            9
          ],
          "drawScale": 1,
          "drawRect": [
            11,
            9,
            363,
            161
          ],
          "registeredCoreCenter": [
            191.5,
            90.5
          ],
          "rootResidualPx": [
            0.5,
            0.5
          ],
          "coreExtentDriftFromReference": [
            0.01846,
            0.04237
          ]
        }
      ]
    },
    {
      "id": "tab",
      "status": "accepted_Unity_shared_registration",
      "referenceState": "normal",
      "logicalCanvas": [
        352,
        154
      ],
      "logicalRoot": [
        176,
        77
      ],
      "logicalAnchor": [
        0.5,
        0.5
      ],
      "referenceBodyRect": [
        21,
        18,
        311,
        118
      ],
      "contentRect": [
        63,
        36,
        227,
        82
      ],
      "contentRectRole": "candidate live-text safe area",
      "hitRect": [
        21,
        18,
        311,
        118
      ],
      "hitShape": "rounded_rect",
      "preferredBodyDisplayBox": [
        220,
        82
      ],
      "sharedDisplayScale": 0.6949153,
      "displayCanvasSize": [
        244.61,
        107.017
      ],
      "scaleRule": "Compute one family scale from the reference body and use it unchanged for all states. Never fit each source/glow bbox separately.",
      "futurePaddingExport": {
        "allowed": true,
        "canvas": [
          352,
          154
        ],
        "placement": "state.drawOffset",
        "resample": false,
        "upscale": false,
        "note": "Future optional RGBA padding only. No padded PNG is produced by this metadata tool."
      },
      "stateFallbacks": {
        "hover": "reuse current semantic state; client color feedback only; no geometry change",
        "focus": "client focus indicator outside contentRect; no artwork rescale",
        "pressed": "reuse current semantic state with client tint; position unchanged",
        "disabled": "reuse current semantic state with client desaturation/opacity; hit disabled"
      },
      "states": [
        {
          "state": "normal",
          "assetId": "ui/buttons/tab-normal",
          "file": "assets/ui/buttons/tab-normal.png",
          "generationRecord": "assets/ui/buttons/tab-normal.png.generation.json",
          "sourceSha256FromManifest": "9082885e3b9c97963a2acd24545ca51fa1fad1d0e0f62da757361f800a13ede7",
          "sourceNativeSize": [
            327,
            133
          ],
          "candidateCoreRect": [
            8,
            8,
            311,
            118
          ],
          "coreCenter": [
            163.5,
            67.0
          ],
          "coreMeasurement": {
            "method": "alpha_threshold_bbox",
            "threshold": 224,
            "thresholdIsArtHeuristic": true,
            "maxAlpha": 255,
            "boundsLTRBByAlpha": {
              "192": [
                7,
                8,
                319,
                126
              ],
              "224": [
                8,
                8,
                319,
                126
              ],
              "240": [
                8,
                8,
                318,
                125
              ]
            },
            "opticalSilhouetteApproved": false
          },
          "status": "accepted_Unity_art",
          "drawOffset": [
            13,
            10
          ],
          "drawScale": 1,
          "drawRect": [
            13,
            10,
            327,
            133
          ],
          "registeredCoreCenter": [
            176.5,
            77.0
          ],
          "rootResidualPx": [
            0.5,
            0.0
          ],
          "coreExtentDriftFromReference": [
            0.0,
            0.0
          ]
        },
        {
          "state": "selected",
          "assetId": "ui/buttons/tab-selected",
          "file": "assets/ui/buttons/tab-selected.png",
          "generationRecord": "assets/ui/buttons/tab-selected.png.generation.json",
          "sourceSha256FromManifest": "cf254f9c84e8059770448aed7eebca898bd588c3de2be822bb91e086f00d906a",
          "sourceNativeSize": [
            335,
            137
          ],
          "candidateCoreRect": [
            8,
            10,
            319,
            118
          ],
          "coreCenter": [
            167.5,
            69.0
          ],
          "coreMeasurement": {
            "method": "alpha_threshold_bbox",
            "threshold": 224,
            "thresholdIsArtHeuristic": true,
            "maxAlpha": 255,
            "boundsLTRBByAlpha": {
              "192": [
                7,
                9,
                328,
                129
              ],
              "224": [
                8,
                10,
                327,
                128
              ],
              "240": [
                8,
                10,
                327,
                128
              ]
            },
            "opticalSilhouetteApproved": false
          },
          "status": "accepted_Unity_art",
          "drawOffset": [
            9,
            8
          ],
          "drawScale": 1,
          "drawRect": [
            9,
            8,
            335,
            137
          ],
          "registeredCoreCenter": [
            176.5,
            77.0
          ],
          "rootResidualPx": [
            0.5,
            0.0
          ],
          "coreExtentDriftFromReference": [
            0.02572,
            0.0
          ]
        }
      ]
    },
    {
      "id": "close",
      "status": "accepted_Unity_shared_registration",
      "referenceState": "normal",
      "logicalCanvas": [
        248,
        246
      ],
      "logicalRoot": [
        124,
        123
      ],
      "logicalAnchor": [
        0.5,
        0.5
      ],
      "referenceBodyRect": [
        17,
        17,
        214,
        212
      ],
      "contentRect": [
        57,
        57,
        134,
        132
      ],
      "contentRectRole": "item/icon area; no separate text on this control",
      "hitRect": [
        17,
        17,
        214,
        212
      ],
      "hitShape": "ellipse",
      "preferredBodyDisplayBox": [
        56,
        56
      ],
      "sharedDisplayScale": 0.2616822,
      "displayCanvasSize": [
        64.897,
        64.374
      ],
      "scaleRule": "Compute one family scale from the reference body and use it unchanged for all states. Never fit each source/glow bbox separately.",
      "futurePaddingExport": {
        "allowed": true,
        "canvas": [
          248,
          246
        ],
        "placement": "state.drawOffset",
        "resample": false,
        "upscale": false,
        "note": "Future optional RGBA padding only. No padded PNG is produced by this metadata tool."
      },
      "stateFallbacks": {
        "hover": "reuse current semantic state; client color feedback only; no geometry change",
        "focus": "client focus indicator outside contentRect; no artwork rescale",
        "disabled": "reuse current semantic state with client desaturation/opacity; hit disabled",
        "selected": "no independent selected art; preserve current semantic state"
      },
      "states": [
        {
          "state": "normal",
          "assetId": "ui/buttons/close-normal",
          "file": "assets/ui/buttons/close-normal.png",
          "generationRecord": "assets/ui/buttons/close-normal.png.generation.json",
          "sourceSha256FromManifest": "65b94aeeabc88acd656419a248e595d0bcb6f507e5ff0f209985af7b30aec884",
          "sourceNativeSize": [
            229,
            229
          ],
          "candidateCoreRect": [
            8,
            9,
            214,
            212
          ],
          "coreCenter": [
            115.0,
            115.0
          ],
          "coreMeasurement": {
            "method": "alpha_threshold_bbox",
            "threshold": 224,
            "thresholdIsArtHeuristic": true,
            "maxAlpha": 255,
            "boundsLTRBByAlpha": {
              "192": [
                8,
                8,
                222,
                221
              ],
              "224": [
                8,
                9,
                222,
                221
              ],
              "240": [
                9,
                10,
                222,
                221
              ]
            },
            "opticalSilhouetteApproved": false
          },
          "status": "accepted_Unity_art",
          "drawOffset": [
            9,
            8
          ],
          "drawScale": 1,
          "drawRect": [
            9,
            8,
            229,
            229
          ],
          "registeredCoreCenter": [
            124.0,
            123.0
          ],
          "rootResidualPx": [
            0.0,
            0.0
          ],
          "coreExtentDriftFromReference": [
            0.0,
            0.0
          ]
        },
        {
          "state": "pressed",
          "assetId": "ui/buttons/close-pressed",
          "file": "assets/ui/buttons/close-pressed.png",
          "generationRecord": "assets/ui/buttons/close-pressed.png.generation.json",
          "sourceSha256FromManifest": "0dd573212396c57ed9b4ffee84ed58498f2f8ac0f0e58e579dc5ae5c7e05b4ae",
          "sourceNativeSize": [
            230,
            228
          ],
          "candidateCoreRect": [
            9,
            8,
            213,
            212
          ],
          "coreCenter": [
            115.5,
            114.0
          ],
          "coreMeasurement": {
            "method": "alpha_threshold_bbox",
            "threshold": 224,
            "thresholdIsArtHeuristic": true,
            "maxAlpha": 255,
            "boundsLTRBByAlpha": {
              "192": [
                8,
                8,
                222,
                220
              ],
              "224": [
                9,
                8,
                222,
                220
              ],
              "240": [
                9,
                8,
                222,
                219
              ]
            },
            "opticalSilhouetteApproved": false
          },
          "status": "accepted_Unity_art",
          "drawOffset": [
            9,
            9
          ],
          "drawScale": 1,
          "drawRect": [
            9,
            9,
            230,
            228
          ],
          "registeredCoreCenter": [
            124.5,
            123.0
          ],
          "rootResidualPx": [
            0.5,
            0.0
          ],
          "coreExtentDriftFromReference": [
            -0.00467,
            0.0
          ]
        }
      ]
    },
    {
      "id": "slot",
      "status": "accepted_Unity_shared_registration",
      "referenceState": "normal",
      "logicalCanvas": [
        310,
        308
      ],
      "logicalRoot": [
        155,
        154
      ],
      "logicalAnchor": [
        0.5,
        0.5
      ],
      "referenceBodyRect": [
        32,
        32,
        246,
        244
      ],
      "contentRect": [
        56,
        56,
        198,
        196
      ],
      "contentRectRole": "item/icon area; no separate text on this control",
      "hitRect": [
        32,
        32,
        246,
        244
      ],
      "hitShape": "rounded_rect",
      "preferredBodyDisplayBox": [
        112,
        112
      ],
      "sharedDisplayScale": 0.4552846,
      "displayCanvasSize": [
        141.138,
        140.228
      ],
      "scaleRule": "Compute one family scale from the reference body and use it unchanged for all states. Never fit each source/glow bbox separately.",
      "futurePaddingExport": {
        "allowed": true,
        "canvas": [
          310,
          308
        ],
        "placement": "state.drawOffset",
        "resample": false,
        "upscale": false,
        "note": "Future optional RGBA padding only. No padded PNG is produced by this metadata tool."
      },
      "stateFallbacks": {
        "hover": "reuse current semantic state; client color feedback only; no geometry change",
        "focus": "client focus indicator outside contentRect; no artwork rescale",
        "pressed": "reuse current semantic state with client tint; position unchanged",
        "disabled": "reuse current semantic state with client desaturation/opacity; hit disabled"
      },
      "states": [
        {
          "state": "normal",
          "assetId": "ui/hud/slot-normal",
          "file": "assets/ui/hud/slot-normal.png",
          "generationRecord": "assets/ui/hud/slot-normal.png.generation.json",
          "sourceSha256FromManifest": "a4524e8f180217a2a3d2c2b5802ba88277567fa5446bcd0e55300fba3ec0527e",
          "sourceNativeSize": [
            261,
            262
          ],
          "candidateCoreRect": [
            8,
            11,
            246,
            244
          ],
          "coreCenter": [
            131.0,
            133.0
          ],
          "coreMeasurement": {
            "method": "alpha_threshold_bbox",
            "threshold": 224,
            "thresholdIsArtHeuristic": true,
            "maxAlpha": 255,
            "boundsLTRBByAlpha": {
              "192": [
                8,
                10,
                254,
                255
              ],
              "224": [
                8,
                11,
                254,
                255
              ],
              "240": [
                8,
                11,
                253,
                255
              ]
            },
            "opticalSilhouetteApproved": false
          },
          "status": "accepted_Unity_art",
          "drawOffset": [
            24,
            21
          ],
          "drawScale": 1,
          "drawRect": [
            24,
            21,
            261,
            262
          ],
          "registeredCoreCenter": [
            155.0,
            154.0
          ],
          "rootResidualPx": [
            0.0,
            0.0
          ],
          "coreExtentDriftFromReference": [
            0.0,
            0.0
          ]
        },
        {
          "state": "selected",
          "assetId": "ui/hud/slot-selected",
          "file": "assets/ui/hud/slot-selected.png",
          "generationRecord": "assets/ui/hud/slot-selected.png.generation.json",
          "sourceSha256FromManifest": "e8a9b6262461f7f72a2975566f281b56019577e76a7d304ecb81e2803562bd25",
          "sourceNativeSize": [
            293,
            288
          ],
          "candidateCoreRect": [
            20,
            19,
            252,
            247
          ],
          "coreCenter": [
            146.0,
            142.5
          ],
          "coreMeasurement": {
            "method": "alpha_threshold_bbox",
            "threshold": 224,
            "thresholdIsArtHeuristic": true,
            "maxAlpha": 254,
            "boundsLTRBByAlpha": {
              "192": [
                19,
                18,
                274,
                267
              ],
              "224": [
                20,
                19,
                272,
                266
              ],
              "240": [
                21,
                20,
                270,
                266
              ]
            },
            "opticalSilhouetteApproved": false
          },
          "status": "accepted_Unity_art",
          "drawOffset": [
            9,
            12
          ],
          "drawScale": 1,
          "drawRect": [
            9,
            12,
            293,
            288
          ],
          "registeredCoreCenter": [
            155.0,
            154.5
          ],
          "rootResidualPx": [
            0.0,
            0.5
          ],
          "coreExtentDriftFromReference": [
            0.02439,
            0.0123
          ]
        },
        {
          "state": "locked",
          "assetId": "ui/hud/slot-locked",
          "file": "assets/ui/hud/slot-locked.png",
          "generationRecord": "assets/ui/hud/slot-locked.png.generation.json",
          "sourceSha256FromManifest": "624c508270584f607041914a1b5136ff8cf0773868d81b36e83d034f4a3ef95d",
          "sourceNativeSize": [
            265,
            263
          ],
          "candidateCoreRect": [
            10,
            11,
            248,
            244
          ],
          "coreCenter": [
            134.0,
            133.0
          ],
          "coreMeasurement": {
            "method": "alpha_threshold_bbox",
            "threshold": 224,
            "thresholdIsArtHeuristic": true,
            "maxAlpha": 255,
            "boundsLTRBByAlpha": {
              "192": [
                10,
                10,
                258,
                256
              ],
              "224": [
                10,
                11,
                258,
                255
              ],
              "240": [
                11,
                11,
                258,
                255
              ]
            },
            "opticalSilhouetteApproved": false
          },
          "status": "accepted_Unity_art",
          "drawOffset": [
            21,
            21
          ],
          "drawScale": 1,
          "drawRect": [
            21,
            21,
            265,
            263
          ],
          "registeredCoreCenter": [
            155.0,
            154.0
          ],
          "rootResidualPx": [
            0.0,
            0.0
          ],
          "coreExtentDriftFromReference": [
            0.00813,
            0.0
          ]
        },
        {
          "state": "empty",
          "assetId": "ui/hud/slot-empty",
          "file": "assets/ui/hud/slot-empty.png",
          "generationRecord": "assets/ui/hud/slot-empty.png.generation.json",
          "sourceSha256FromManifest": "837b0bdbb9ea0ccc081fc3a25bfc5d5e7062bd0b759918c70469bb0bb887f0d1",
          "sourceNativeSize": [
            267,
            262
          ],
          "candidateCoreRect": [
            8,
            10,
            246,
            245
          ],
          "coreCenter": [
            131.0,
            132.5
          ],
          "coreMeasurement": {
            "method": "alpha_threshold_bbox",
            "threshold": 224,
            "thresholdIsArtHeuristic": true,
            "maxAlpha": 255,
            "boundsLTRBByAlpha": {
              "192": [
                7,
                9,
                254,
                255
              ],
              "224": [
                8,
                10,
                254,
                255
              ],
              "240": [
                8,
                10,
                254,
                254
              ]
            },
            "opticalSilhouetteApproved": false
          },
          "status": "accepted_Unity_art",
          "drawOffset": [
            24,
            22
          ],
          "drawScale": 1,
          "drawRect": [
            24,
            22,
            267,
            262
          ],
          "registeredCoreCenter": [
            155.0,
            154.5
          ],
          "rootResidualPx": [
            0.0,
            0.5
          ],
          "coreExtentDriftFromReference": [
            0.0,
            0.0041
          ]
        }
      ]
    },
    {
      "id": "toggle",
      "status": "accepted_Unity_shared_registration",
      "referenceState": "off",
      "logicalCanvas": [
        302,
        166
      ],
      "logicalRoot": [
        151,
        83
      ],
      "logicalAnchor": [
        0.5,
        0.5
      ],
      "referenceBodyRect": [
        17,
        22,
        269,
        123
      ],
      "contentRect": [
        35,
        40,
        233,
        87
      ],
      "contentRectRole": "item/icon area; no separate text on this control",
      "hitRect": [
        17,
        22,
        269,
        123
      ],
      "hitShape": "rounded_rect",
      "preferredBodyDisplayBox": [
        88,
        44
      ],
      "sharedDisplayScale": 0.3271375,
      "displayCanvasSize": [
        98.796,
        54.305
      ],
      "scaleRule": "Compute one family scale from the reference body and use it unchanged for all states. Never fit each source/glow bbox separately.",
      "futurePaddingExport": {
        "allowed": true,
        "canvas": [
          302,
          166
        ],
        "placement": "state.drawOffset",
        "resample": false,
        "upscale": false,
        "note": "Future optional RGBA padding only. No padded PNG is produced by this metadata tool."
      },
      "stateFallbacks": {
        "hover": "reuse current semantic state; client color feedback only; no geometry change",
        "focus": "client focus indicator outside contentRect; no artwork rescale",
        "pressed": "reuse current semantic state with client tint; position unchanged",
        "disabled": "reuse current semantic state with client desaturation/opacity; hit disabled",
        "selected": "no independent selected art; preserve current semantic state"
      },
      "states": [
        {
          "state": "off",
          "assetId": "ui/hud/toggle-off",
          "file": "assets/ui/hud/toggle-off.png",
          "generationRecord": "assets/ui/hud/toggle-off.png.generation.json",
          "sourceSha256FromManifest": "fe4ffc89c5049cf06b9bc030c89cd5fe961ad01f1695587772929c2b491a6129",
          "sourceNativeSize": [
            285,
            145
          ],
          "candidateCoreRect": [
            8,
            9,
            269,
            123
          ],
          "coreCenter": [
            142.5,
            70.5
          ],
          "coreMeasurement": {
            "method": "alpha_threshold_bbox",
            "threshold": 224,
            "thresholdIsArtHeuristic": true,
            "maxAlpha": 255,
            "boundsLTRBByAlpha": {
              "192": [
                8,
                9,
                277,
                132
              ],
              "224": [
                8,
                9,
                277,
                132
              ],
              "240": [
                8,
                10,
                277,
                132
              ]
            },
            "opticalSilhouetteApproved": false
          },
          "status": "accepted_Unity_art",
          "drawOffset": [
            9,
            13
          ],
          "drawScale": 1,
          "drawRect": [
            9,
            13,
            285,
            145
          ],
          "registeredCoreCenter": [
            151.5,
            83.5
          ],
          "rootResidualPx": [
            0.5,
            0.5
          ],
          "coreExtentDriftFromReference": [
            0.0,
            0.0
          ]
        },
        {
          "state": "on",
          "assetId": "ui/hud/toggle-on",
          "file": "assets/ui/hud/toggle-on.png",
          "generationRecord": "assets/ui/hud/toggle-on.png.generation.json",
          "sourceSha256FromManifest": "9ec0a2ed6831f36ccd6097ccfe3b23fb10b65f5d651432828b4233099f701f00",
          "sourceNativeSize": [
            280,
            144
          ],
          "candidateCoreRect": [
            8,
            8,
            264,
            124
          ],
          "coreCenter": [
            140.0,
            70.0
          ],
          "coreMeasurement": {
            "method": "alpha_threshold_bbox",
            "threshold": 224,
            "thresholdIsArtHeuristic": true,
            "maxAlpha": 255,
            "boundsLTRBByAlpha": {
              "192": [
                8,
                8,
                272,
                132
              ],
              "224": [
                8,
                8,
                272,
                132
              ],
              "240": [
                8,
                8,
                272,
                131
              ]
            },
            "opticalSilhouetteApproved": false
          },
          "status": "accepted_Unity_art",
          "drawOffset": [
            11,
            13
          ],
          "drawScale": 1,
          "drawRect": [
            11,
            13,
            280,
            144
          ],
          "registeredCoreCenter": [
            151.0,
            83.0
          ],
          "rootResidualPx": [
            0.0,
            0.0
          ],
          "coreExtentDriftFromReference": [
            -0.01859,
            0.00813
          ]
        }
      ]
    },
    {
      "id": "checkbox",
      "status": "accepted_Unity_shared_registration",
      "referenceState": "off",
      "logicalCanvas": [
        230,
        224
      ],
      "logicalRoot": [
        115,
        112
      ],
      "logicalAnchor": [
        0.5,
        0.5
      ],
      "referenceBodyRect": [
        16,
        20,
        198,
        185
      ],
      "contentRect": [
        40,
        44,
        150,
        137
      ],
      "contentRectRole": "item/icon area; no separate text on this control",
      "hitRect": [
        16,
        20,
        198,
        185
      ],
      "hitShape": "rounded_rect",
      "preferredBodyDisplayBox": [
        38,
        38
      ],
      "sharedDisplayScale": 0.1919192,
      "displayCanvasSize": [
        44.141,
        42.99
      ],
      "scaleRule": "Compute one family scale from the reference body and use it unchanged for all states. Never fit each source/glow bbox separately.",
      "futurePaddingExport": {
        "allowed": true,
        "canvas": [
          230,
          224
        ],
        "placement": "state.drawOffset",
        "resample": false,
        "upscale": false,
        "note": "Future optional RGBA padding only. No padded PNG is produced by this metadata tool."
      },
      "stateFallbacks": {
        "hover": "reuse current semantic state; client color feedback only; no geometry change",
        "focus": "client focus indicator outside contentRect; no artwork rescale",
        "pressed": "reuse current semantic state with client tint; position unchanged",
        "disabled": "reuse current semantic state with client desaturation/opacity; hit disabled",
        "selected": "no independent selected art; preserve current semantic state"
      },
      "states": [
        {
          "state": "off",
          "assetId": "ui/hud/checkbox-off",
          "file": "assets/ui/hud/checkbox-off.png",
          "generationRecord": "assets/ui/hud/checkbox-off.png.generation.json",
          "sourceSha256FromManifest": "1f8f5aaf04d2bb60c5c3e3c538e1dd3d1fdf1d57c1fbe3c4f5b45ad013be86fc",
          "sourceNativeSize": [
            214,
            202
          ],
          "candidateCoreRect": [
            8,
            9,
            198,
            185
          ],
          "coreCenter": [
            107.0,
            101.5
          ],
          "coreMeasurement": {
            "method": "alpha_threshold_bbox",
            "threshold": 224,
            "thresholdIsArtHeuristic": true,
            "maxAlpha": 255,
            "boundsLTRBByAlpha": {
              "192": [
                8,
                8,
                207,
                194
              ],
              "224": [
                8,
                9,
                206,
                194
              ],
              "240": [
                8,
                9,
                206,
                194
              ]
            },
            "opticalSilhouetteApproved": false
          },
          "status": "accepted_Unity_art",
          "drawOffset": [
            8,
            11
          ],
          "drawScale": 1,
          "drawRect": [
            8,
            11,
            214,
            202
          ],
          "registeredCoreCenter": [
            115.0,
            112.5
          ],
          "rootResidualPx": [
            0.0,
            0.5
          ],
          "coreExtentDriftFromReference": [
            0.0,
            0.0
          ]
        },
        {
          "state": "on",
          "assetId": "ui/hud/checkbox-on",
          "file": "assets/ui/hud/checkbox-on.png",
          "generationRecord": "assets/ui/hud/checkbox-on.png.generation.json",
          "sourceSha256FromManifest": "a3fd44e00e3b9657f20e49e65da08d70c50cc2aef75a3535fab4febe0cd5a372",
          "sourceNativeSize": [
            209,
            206
          ],
          "candidateCoreRect": [
            8,
            11,
            193,
            186
          ],
          "coreCenter": [
            104.5,
            104.0
          ],
          "coreMeasurement": {
            "method": "alpha_threshold_bbox",
            "threshold": 224,
            "thresholdIsArtHeuristic": true,
            "maxAlpha": 255,
            "boundsLTRBByAlpha": {
              "192": [
                7,
                11,
                202,
                197
              ],
              "224": [
                8,
                11,
                201,
                197
              ],
              "240": [
                8,
                12,
                201,
                197
              ]
            },
            "opticalSilhouetteApproved": false
          },
          "status": "accepted_Unity_art",
          "drawOffset": [
            11,
            8
          ],
          "drawScale": 1,
          "drawRect": [
            11,
            8,
            209,
            206
          ],
          "registeredCoreCenter": [
            115.5,
            112.0
          ],
          "rootResidualPx": [
            0.5,
            0.0
          ],
          "coreExtentDriftFromReference": [
            -0.02525,
            0.00541
          ]
        }
      ]
    },
    {
      "id": "slider-thumb",
      "status": "accepted_Unity_shared_registration",
      "referenceState": "normal",
      "logicalCanvas": [
        406,
        402
      ],
      "logicalRoot": [
        203,
        201
      ],
      "logicalAnchor": [
        0.5,
        0.5
      ],
      "referenceBodyRect": [
        17,
        15,
        373,
        372
      ],
      "contentRect": [
        89,
        87,
        229,
        228
      ],
      "contentRectRole": "item/icon area; no separate text on this control",
      "hitRect": [
        17,
        15,
        373,
        372
      ],
      "hitShape": "ellipse",
      "preferredBodyDisplayBox": [
        40,
        40
      ],
      "sharedDisplayScale": 0.1072386,
      "displayCanvasSize": [
        43.539,
        43.11
      ],
      "scaleRule": "Compute one family scale from the reference body and use it unchanged for all states. Never fit each source/glow bbox separately.",
      "futurePaddingExport": {
        "allowed": true,
        "canvas": [
          406,
          402
        ],
        "placement": "state.drawOffset",
        "resample": false,
        "upscale": false,
        "note": "Future optional RGBA padding only. No padded PNG is produced by this metadata tool."
      },
      "stateFallbacks": {
        "hover": "reuse current semantic state; client color feedback only; no geometry change",
        "focus": "client focus indicator outside contentRect; no artwork rescale",
        "disabled": "reuse current semantic state with client desaturation/opacity; hit disabled",
        "selected": "no independent selected art; preserve current semantic state"
      },
      "states": [
        {
          "state": "normal",
          "assetId": "ui/additions/slider-thumb-normal",
          "file": "assets/ui/additions/slider-thumb-normal.png",
          "generationRecord": "assets/ui/additions/slider-thumb-normal.png.generation.json",
          "sourceSha256FromManifest": "296f5941d06b7b00157e04b68fa298f3911ec638127432a33297459e137efa04",
          "sourceNativeSize": [
            388,
            385
          ],
          "candidateCoreRect": [
            7,
            7,
            373,
            372
          ],
          "coreCenter": [
            193.5,
            193.0
          ],
          "coreMeasurement": {
            "method": "alpha_threshold_bbox",
            "threshold": 224,
            "thresholdIsArtHeuristic": true,
            "maxAlpha": 255,
            "boundsLTRBByAlpha": {
              "192": [
                7,
                6,
                380,
                380
              ],
              "224": [
                7,
                7,
                380,
                379
              ],
              "240": [
                7,
                7,
                380,
                379
              ]
            },
            "opticalSilhouetteApproved": false
          },
          "status": "accepted_Unity_art",
          "drawOffset": [
            10,
            8
          ],
          "drawScale": 1,
          "drawRect": [
            10,
            8,
            388,
            385
          ],
          "registeredCoreCenter": [
            203.5,
            201.0
          ],
          "rootResidualPx": [
            0.5,
            0.0
          ],
          "coreExtentDriftFromReference": [
            0.0,
            0.0
          ]
        },
        {
          "state": "pressed",
          "assetId": "ui/additions/slider-thumb-pressed",
          "file": "assets/ui/additions/slider-thumb-pressed.png",
          "generationRecord": "assets/ui/additions/slider-thumb-pressed.png.generation.json",
          "sourceSha256FromManifest": "149de357b7a50e1d59dedf99c86ed16952d5bc24c6c6b2d2304ef9ab71693094",
          "sourceNativeSize": [
            387,
            384
          ],
          "candidateCoreRect": [
            6,
            6,
            373,
            372
          ],
          "coreCenter": [
            192.5,
            192.0
          ],
          "coreMeasurement": {
            "method": "alpha_threshold_bbox",
            "threshold": 224,
            "thresholdIsArtHeuristic": true,
            "maxAlpha": 255,
            "boundsLTRBByAlpha": {
              "192": [
                6,
                5,
                380,
                379
              ],
              "224": [
                6,
                6,
                379,
                378
              ],
              "240": [
                7,
                6,
                379,
                378
              ]
            },
            "opticalSilhouetteApproved": false
          },
          "status": "accepted_Unity_art",
          "drawOffset": [
            11,
            9
          ],
          "drawScale": 1,
          "drawRect": [
            11,
            9,
            387,
            384
          ],
          "registeredCoreCenter": [
            203.5,
            201.0
          ],
          "rootResidualPx": [
            0.5,
            0.0
          ],
          "coreExtentDriftFromReference": [
            0.0,
            0.0
          ]
        }
      ]
    }
  ],
  "warnings": [
    {
      "id": "source_state_core_shape_drift",
      "family": "primary",
      "state": "selected",
      "assetId": "ui/buttons/primary-selected",
      "relativeWidthHeight": [
        0.00912,
        0.05085
      ],
      "threshold": 0.03,
      "meaning": "Alpha heuristic sees native extent differences after registration; candidate for flicker review, not anatomy/art approval."
    },
    {
      "id": "source_state_core_shape_drift",
      "family": "secondary",
      "state": "selected",
      "assetId": "ui/buttons/secondary-selected",
      "relativeWidthHeight": [
        0.01846,
        0.04237
      ],
      "threshold": 0.03,
      "meaning": "Alpha heuristic sees native extent differences after registration; candidate for flicker review, not anatomy/art approval."
    }
  ],
  "acceptancePending": [],
  "finalAcceptance": "docs/UNITY_FINAL_ACCEPTANCE.json"
};
