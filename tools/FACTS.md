# معلومة اليوم — TikTok و YouTube Shorts

محتوى مستقل تماماً عن صفحة الحِكم في إنستغرام: فيديو قصير يومي (1080×1920، حوالي 13 ثانية) بمعلومة عامة مدهشة وموثّقة، بالعربية.
ينشر على الحسابين الشخصيين للمستخدم المربوطين بنفس علامة Metricool: TikTok (brhim448) و YouTube (قناة BRAHIM DIAN). لا يُنشر على إنستغرام.

## الإعدادات

- Metricool: blogId `7614173`، المنطقة الزمنية `Africa/El_Aaiun`.
- موعد النشر: **19:00** يومياً.
- المولّد: `python3 tools/fact.py fact.json videos/fact-YYYY-MM-DD.mp4 --still videos/fact-YYYY-MM-DD.jpg`
  (يحتاج خط Cairo: `GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 --filter=blob:none --sparse https://github.com/google/fonts /home/claude/gfonts && git -C /home/claude/gfonts sparse-checkout set ofl/cairo ofl/amiri`)
- الرابط العام للفيديو: `https://raw.githubusercontent.com/brahimdiane-gif/hikma-images/main/videos/fact-YYYY-MM-DD.mp4`
- السجل: `facts_log.md` في جذر المستودع — اقرأه لتجنب التكرار ولمعرفة رقم الحلقة التالي، ثم أضف سطراً: `- YYYY-MM-DD — رقم N — الفئة — المعلومة باختصار — المصدر (الرابط)`.

## الفئات حسب اليوم

| اليوم | الفئة | palette |
|---|---|---|
| الإثنين | جسم الإنسان | rose |
| الثلاثاء | التاريخ | sand |
| الأربعاء | الحيوانات | mint |
| الخميس | الفضاء | sky |
| الجمعة | اللغة العربية | violet |
| السبت | المغرب (تاريخه وجغرافيته وتراثه) | sun |
| الأحد | العلوم والاختراعات | sea |

## الدقة (شرط مطلق)

- كل معلومة تُتحقق منها ببحث ويب من مصدرين موثوقين على الأقل (موسوعات، مؤسسات علمية مثل NASA و WHO و National Geographic و Britannica، جامعات، مصادر رسمية مغربية). اذكر أوثقهما في الحقل `source` باسم قصير.
- تجنّب الخرافات المنتشرة («نستخدم 10% من دماغنا»، «سور الصين يُرى من الفضاء»…)، والأرقام غير المؤكدة، والمواضيع الدينية والسياسية والطبية العلاجية.
- إن كان في الرقم خلاف، استعمل «نحو» أو «حوالي» أو اختر معلومة أخرى.
- الأرقام لاتينية (0–9).

## كتابة المعلومة

- `hook`: «هل تعلم؟» غالباً، أو بديل قصير جذاب يناسب المعلومة («معلومة ستدهشك»، «سؤال سريع:»).
- `lines`: من 3 إلى 5 أسطر، 4–7 كلمات للسطر، بلغة عربية فصيحة بسيطة. السطر الأخير يحمل المفاجأة أو الخلاصة.
- `number`: رقم الحلقة التالي من facts_log.md (يبدأ من 1).
- افتح الصورة الثابتة (--still) بأداة Read وتأكد أن كل النص ظاهر وغير مقصوص.

## النشر في Metricool (منشور واحد للمنصتين)

```
blogId "7614173", date "YYYY-MM-DDT19:00:00+00:00", info:
{"autoPublish": true, "draft": false, "descendants": [], "firstCommentText": "", "hasNotReadNotes": false,
 "media": ["<رابط الفيديو>"], "mediaAltText": [], "providers": [{"network": "tiktok"}, {"network": "youtube"}],
 "publicationDate": {"dateTime": "YYYY-MM-DDT19:00:00", "timezone": "Africa/El_Aaiun"},
 "shortener": false, "smartLinkData": {"ids": []}, "text": "<الوصف>",
 "tiktokData": {"privacyOption": "PUBLIC_TO_EVERYONE", "disableComment": false, "disableDuet": false, "disableStitch": false, "autoAddMusic": false, "commercialContentThirdParty": false, "commercialContentOwnBrand": false},
 "youtubeData": {"title": "<العنوان>", "type": "short", "privacy": "public", "madeForKids": false, "category": "EDUCATION", "tags": [<5-8 كلمات>]}}
```

- **العنوان (YouTube)**: أقل من 70 حرفاً، يثير الفضول دون مبالغة كاذبة، وينتهي بـ ` #shorts`. مثال: «لماذا ترى الشمس دائماً في الماضي؟ #shorts».
- **الوصف (text)**: سطر يلخص المعلومة، ثم سؤال للتعليق («هل كنت تعرف هذا؟»)، ثم «المصدر: …»، ثم 4–6 وسوم: `#معلومة_اليوم #هل_تعلم` + وسوم الفئة (مثل `#الفضاء #علوم`).
- إن فشلت منصة واحدة، أعد المحاولة بمنشور منفصل للمنصة الأخرى فقط، ولا تكرر النشر على المنصة التي نجحت.
- إن كان الموعد قد مضى، اجعله بعد 5 دقائق.

## بعد النشر

أرسل الفيديو بـ SendUserFile (status: proactive) مع سطر: الفئة، رقم الحلقة، موعد النشر. ثم بـ SendUserMessage: العنوان والوصف والمصدر مع رابطه. إن فشل أي جزء، أرسل الفيديو والنصوص مع سبب الخطأ باختصار ليتمكن من النشر يدوياً.
