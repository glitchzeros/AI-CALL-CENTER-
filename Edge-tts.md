# edge-tts

`edge-tts` is a Python module that allows you to use Microsoft Edge's online text-to-speech service from within your Python code or using the provided `edge-tts` or `edge-playback` command.

## Installation

To install it, run the following command:

    $ pip install edge-tts

If you only want to use the `edge-tts` and `edge-playback` commands, it would be better to use `pipx`:

    $ pipx install edge-tts

## Usage

### Basic usage

If you want to use the `edge-tts` command, you can simply run it with the following command:

    $ edge-tts --text "Hello, world!" --write-media hello.mp3 --write-subtitles hello.srt

If you wish to play it back immediately with subtitles, you could use the `edge-playback` command:

    $ edge-playback --text "Hello, world!"

Note that `edge-playback` requires the installation of the [`mpv` command line player](https://mpv.io/), except on Windows.

All `edge-tts` commands work with `edge-playback` with the exception of the `--write-media`, `--write-subtitles` and `--list-voices` options.

### Changing the voice

You can change the voice used by the text-to-speech service by using the `--voice` option. The `--list-voices` option can be used to list all available voices.

    $ edge-tts --list-voices
    Name                               Gender    ContentCategories      VoicePersonalities
    ---------------------------------  --------  ---------------------  --------------------------------------
                       "af-ZA-AdriNeural"  , "af-ZA-WillemNeural", "sq-AL-AnilaNeural", "sq-AL-IlirNeural",
            "am-ET-AmehaNeural", "am-ET-MekdesNeural", "ar-DZ-AminaNeural", "ar-DZ-IsmaelNeural",
            "ar-BH-AliNeural", "ar-BH-LailaNeural", "ar-EG-SalmaNeural", "ar-EG-ShakirNeural",
            "ar-IQ-BasselNeural", "ar-IQ-RanaNeural", "ar-JO-SanaNeural", "ar-JO-TaimNeural",
            "ar-KW-FahedNeural", "ar-KW-NouraNeural", "ar-LB-LaylaNeural", "ar-LB-RamiNeural",
            "ar-LY-ImanNeural", "ar-LY-OmarNeural", "ar-MA-JamalNeural", "ar-MA-MounaNeural",
            "ar-OM-AbdullahNeural", "ar-OM-AyshaNeural", "ar-QA-AmalNeural", "ar-QA-MoazNeural",
            "ar-SA-HamedNeural", "ar-SA-ZariyahNeural", "ar-SY-AmanyNeural", "ar-SY-LaithNeural",
            "ar-TN-HediNeural", "ar-TN-ReemNeural", "ar-AE-FatimaNeural", "ar-AE-HamdanNeural",
            "ar-YE-MaryamNeural", "ar-YE-SalehNeural", "az-AZ-BabekNeural", "az-AZ-BanuNeural",
            "bn-BD-NabanitaNeural", "bn-BD-PradeepNeural", "bn-IN-BashkarNeural", "bn-IN-TanishaaNeural",
            "bs-BA-GoranNeural", "bs-BA-VesnaNeural", "bg-BG-BorislavNeural", "bg-BG-KalinaNeural",
            "my-MM-NilarNeural", "my-MM-ThihaNeural", "ca-ES-EnricNeural", "ca-ES-JoanaNeural",
            "zh-HK-HiuGaaiNeural", "zh-HK-HiuMaanNeural", "zh-HK-WanLungNeural", "zh-CN-XiaoxiaoNeural",
            "zh-CN-XiaoyiNeural", "zh-CN-YunjianNeural", "zh-CN-YunxiNeural", "zh-CN-YunxiaNeural",
            "zh-CN-YunyangNeural", "zh-CN-liaoning-XiaobeiNeural", "zh-TW-HsiaoChenNeural",
            "zh-TW-YunJheNeural", "zh-TW-HsiaoYuNeural", "zh-CN-shaanxi-XiaoniNeural",
            "hr-HR-GabrijelaNeural", "hr-HR-SreckoNeural", "cs-CZ-AntoninNeural", "cs-CZ-VlastaNeural",
            "da-DK-ChristelNeural", "da-DK-JeppeNeural", "nl-BE-ArnaudNeural", "nl-BE-DenaNeural",
            "nl-NL-ColetteNeural", "nl-NL-FennaNeural", "nl-NL-MaartenNeural", "en-AU-NatashaNeural",
            "en-AU-WilliamNeural", "en-CA-ClaraNeural", "en-CA-LiamNeural", "en-HK-SamNeural",
            "en-HK-YanNeural", "en-IN-NeerjaExpressiveNeural", "en-IN-NeerjaNeural", "en-IN-PrabhatNeural",
            "en-IE-ConnorNeural", "en-IE-EmilyNeural",
            "en-KE-AsiliaNeural", "en-KE-ChilembaNeural",
            "en-NZ-MitchellNeural", "en-NZ-MollyNeural", "en-NG-AbeoNeural", "en-NG-EzinneNeural",
            "en-PH-JamesNeural", "en-PH-RosaNeural", "en-SG-LunaNeural", "en-SG-WayneNeural",
            "en-ZA-LeahNeural", "en-ZA-LukeNeural", "en-TZ-ElimuNeural", "en-TZ-ImaniNeural",
            "en-GB-LibbyNeural", "en-GB-MaisieNeural", "en-GB-RyanNeural", "en-GB-SoniaNeural",
            "en-GB-ThomasNeural", "en-US-AnaNeural", "en-US-AriaNeural", "en-US-ChristopherNeural",
            "en-US-EricNeural", "en-US-GuyNeural", "en-US-JennyNeural", "en-US-MichelleNeural",
            "en-US-RogerNeural", "en-US-SteffanNeural", "et-EE-AnuNeural", "et-EE-KertNeural",
            "fil-PH-AngeloNeural", "fil-PH-BlessicaNeural", "fi-FI-HarriNeural", "fi-FI-NooraNeural",
            "fr-BE-CharlineNeural", "fr-BE-GerardNeural", "fr-CA-ThierryNeural", "fr-CA-AntoineNeural",
            "fr-CA-JeanNeural", "fr-CA-SylvieNeural", "fr-FR-VivienneMultilingualNeural",
            "fr-FR-RemyMultilingualNeural", "fr-FR-DeniseNeural", "fr-FR-EloiseNeural", "fr-FR-HenriNeural",
            "fr-CH-ArianeNeural", "fr-CH-FabriceNeural", "gl-ES-RoiNeural", "gl-ES-SabelaNeural",
            "ka-GE-EkaNeural", "ka-GE-GiorgiNeural", "de-AT-IngridNeural", "de-AT-JonasNeural",
            "de-DE-SeraphinaMultilingualNeural", "de-DE-FlorianMultilingualNeural", "de-DE-AmalaNeural",
            "de-DE-ConradNeural", "de-DE-KatjaNeural", "de-DE-KillianNeural",
            "de-CH-JanNeural", "de-CH-LeniNeural", "el-GR-AthinaNeural", "el-GR-NestorasNeural", "gu-IN-DhwaniNeural",
            "gu-IN-NiranjanNeural", "he-IL-AvriNeural", "he-IL-HilaNeural", "hi-IN-MadhurNeural",
            "hi-IN-SwaraNeural", "hu-HU-NoemiNeural", "hu-HU-TamasNeural", "is-IS-GudrunNeural",
            "is-IS-GunnarNeural", "id-ID-ArdiNeural", "id-ID-GadisNeural", "ga-IE-ColmNeural",
            "ga-IE-OrlaNeural", "it-IT-GiuseppeNeural", "it-IT-DiegoNeural", "it-IT-ElsaNeural",
            "it-IT-IsabellaNeural", "ja-JP-KeitaNeural", "ja-JP-NanamiNeural", "jv-ID-DimasNeural",
            "jv-ID-SitiNeural", "kn-IN-GaganNeural", "kn-IN-SapnaNeural", "kk-KZ-AigulNeural",
            "kk-KZ-DauletNeural", "km-KH-PisethNeural", "km-KH-SreymomNeural", "ko-KR-HyunsuNeural",
            "ko-KR-InJoonNeural", "ko-KR-SunHiNeural", "lo-LA-ChanthavongNeural", "lo-LA-KeomanyNeural",
            "lv-LV-EveritaNeural", "lv-LV-NilsNeural", "lt-LT-LeonasNeural", "lt-LT-OnaNeural",
            "mk-MK-AleksandarNeural", "mk-MK-MarijaNeural", "ms-MY-OsmanNeural", "ms-MY-YasminNeural",
            "ml-IN-MidhunNeural", "ml-IN-SobhanaNeural", "mt-MT-GraceNeural", "mt-MT-JosephNeural",
            "mr-IN-AarohiNeural", "mr-IN-ManoharNeural", "mn-MN-BataaNeural", "mn-MN-YesuiNeural",
            "ne-NP-HemkalaNeural", "ne-NP-SagarNeural", "nb-NO-FinnNeural", "nb-NO-PernilleNeural",
            "ps-AF-GulNawazNeural", "ps-AF-LatifaNeural", "fa-IR-DilaraNeural", "fa-IR-FaridNeural",
            "pl-PL-MarekNeural", "pl-PL-ZofiaNeural", "pt-BR-ThalitaNeural", "pt-BR-AntonioNeural",
            "pt-BR-FranciscaNeural", "pt-PT-DuarteNeural", "pt-PT-RaquelNeural", "ro-RO-AlinaNeural",
            "ro-RO-EmilNeural", "ru-RU-DmitryNeural", "ru-RU-SvetlanaNeural", "sr-RS-NicholasNeural",
            "sr-RS-SophieNeural", "si-LK-SameeraNeural", "si-LK-ThiliniNeural", "sk-SK-LukasNeural",
            "sk-SK-ViktoriaNeural", "sl-SI-PetraNeural", "sl-SI-RokNeural", "so-SO-MuuseNeural",
            "so-SO-UbaxNeural", "es-AR-ElenaNeural", "es-AR-TomasNeural", "es-BO-MarceloNeural",
            "es-BO-SofiaNeural", "es-CL-CatalinaNeural", "es-CL-LorenzoNeural", "es-ES-XimenaNeural",
            "es-CO-GonzaloNeural", "es-CO-SalomeNeural", "es-CR-JuanNeural", "es-CR-MariaNeural",
            "es-CU-BelkysNeural", "es-CU-ManuelNeural", "es-DO-EmilioNeural", "es-DO-RamonaNeural",
            "es-EC-AndreaNeural", "es-EC-LuisNeural", "es-SV-LorenaNeural", "es-SV-RodrigoNeural",
            "es-GQ-JavierNeural", "es-GQ-TeresaNeural", "es-GT-AndresNeural", "es-GT-MartaNeural",
            "es-HN-CarlosNeural", "es-HN-KarlaNeural", "es-MX-DaliaNeural", "es-MX-JorgeNeural",
            "es-NI-FedericoNeural", "es-NI-YolandaNeural", "es-PA-MargaritaNeural", "es-PA-RobertoNeural",
            "es-PY-MarioNeural", "es-PY-TaniaNeural", "es-PE-AlexNeural", "es-PE-CamilaNeural",
            "es-PR-KarinaNeural", "es-PR-VictorNeural", "es-ES-AlvaroNeural", "es-ES-ElviraNeural",
            "es-US-AlonsoNeural", "es-US-PalomaNeural", "es-UY-MateoNeural", "es-UY-ValentinaNeural",
            "es-VE-PaolaNeural", "es-VE-SebastianNeural", "su-ID-JajangNeural", "su-ID-TutiNeural",
            "sw-KE-RafikiNeural", "sw-KE-ZuriNeural", "sw-TZ-DaudiNeural", "sw-TZ-RehemaNeural",
            "sv-SE-MattiasNeural", "sv-SE-SofieNeural", "ta-IN-PallaviNeural", "ta-IN-ValluvarNeural",
            "ta-MY-KaniNeural", "ta-MY-SuryaNeural", "ta-SG-AnbuNeural", "ta-SG-VenbaNeural",
            "ta-LK-KumarNeural", "ta-LK-SaranyaNeural", "te-IN-MohanNeural", "te-IN-ShrutiNeural",
            "th-TH-NiwatNeural", "th-TH-PremwadeeNeural", "tr-TR-AhmetNeural", "tr-TR-EmelNeural",
            "uk-UA-OstapNeural", "uk-UA-PolinaNeural", "ur-IN-GulNeural", "ur-IN-SalmanNeural",
            "ur-PK-AsadNeural", "ur-PK-UzmaNeural", "uz-UZ-SardorNeural", "uz-UZ-MadinaNeural",
            "vi-VN-HoaiMyNeural", "vi-VN-NamMinhNeural", "cy-GB-AledNeural", "cy-GB-NiaNeural",
            "zu-ZA-ThandoNeural", "zu-ZA-ThembaNeural"
           Female    General                Friendly, Positive
    ...

    $ edge-tts --voice ar-EG-SalmaNeural --text "مرحبا كيف حالك؟" --write-media hello_in_arabic.mp3 --write-subtitles hello_in_arabic.srt

### Custom SSML

Support for custom SSML was removed because Microsoft prevents the use of any SSML that could not be generated by Microsoft Edge itself. This means that all the cases where custom SSML would be useful cannot be supported as the service only permits a single `<voice>` tag with a single `<prosody>` tag inside it. Any available customization options that could be used in the `<prosody>` tag are already available from the library or the command line itself.

### Changing rate, volume and pitch

You can change the rate, volume and pitch of the generated speech by using the `--rate`, `--volume` and `--pitch` options. When using a negative value, you will need to use `--[option]=-50%` instead of `--[option] -50%` to avoid the option being interpreted as a command line option.

    $ edge-tts --rate=-50% --text "Hello, world!" --write-media hello_with_rate_lowered.mp3 --write-subtitles hello_with_rate_lowered.srt
    $ edge-tts --volume=-50% --text "Hello, world!" --write-media hello_with_volume_lowered.mp3 --write-subtitles hello_with_volume_lowered.srt
    $ edge-tts --pitch=-50Hz --text "Hello, world!" --write-media hello_with_pitch_lowered.mp3 --write-subtitles hello_with_pitch_lowered.srt

## Python module

It is possible to use the `edge-tts` module directly from Python. Examples from the project itself include:

* [/examples/](/examples/)
* [/src/edge_tts/util.py](/src/edge_tts/util.py)

Other projects that use the `edge-tts` module include:

* [hass-edge-tts](https://github.com/hasscc/hass-edge-tts/blob/main/custom_components/edge_tts/tts.py)
* [Podcastfy](https://github.com/souzatharsis/podcastfy/blob/main/podcastfy/tts/providers/edge.py)
* [tts-samples](https://github.com/yaph/tts-samples/blob/main/bin/create_sound_samples.py) - a collection of [mp3 sound samples](https://github.com/yaph/tts-samples/tree/main/mp3) to facilitate picking a voice for your project.
