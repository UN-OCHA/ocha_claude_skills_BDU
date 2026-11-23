# BDU mockup library: survey

Every template in the full BDU library (`Design/Resources/PS/mockup`, 105 files) was opened, its
slots read, and the untouched template rendered and compared with the preview Photoshop saved in
the file (20 October 2026). **faithful**: indistinguishable. **close**: small colour differences.
Curved pages (Photoshop custom warps) are supported. Archives (.zip, .rar) were not opened.

The curated set (in `mockups/`, see SKILL.md) is marked with its key. Anything else can be used
by path (`render "/path/to/file.psd" …`); check it first with `inspect` and `check`.

| Template | Canvas | Design slots | Result |
|---|---|---|---|
| 01_Phones/Animated_Iphone GIF/Animated_Mockup.psd | 1200×900 | 2: 0.562 persp., 0.562 persp. | faithful |
| 01_Phones/Animated_Iphone GIF/Behance Behance.psd | 1400×10271 | 10: 0.619 persp., 1.007, 1.333 persp., 1.6 curved persp., 0.756 persp., 5.532, 1.6, 1.868 persp., 1.914 persp., 1.778 persp. | faithful |
| 01_Phones/Iphone5_Hand/iphone5-white-hand.psd | 1200×1268 | 1: 0.563 persp. | renders differently from Photoshop |
| 01_Phones/Iphone5_Hands/iphone-410324.psd | 2180×1453 | 1: 0.562 curved persp. | faithful |
| 01_Phones/Mobile-App-Screens-Mockup/Mobile-App-Screen-Mockups.psd | 4500×3000 | 5: 0.562 persp., 0.562 persp., 0.562 persp., 0.562 persp., 0.562 persp. | close |
| 01_Phones/iPhone 6 + Macbook.psd | 3600×2400 | 1: 0.562 persp. | faithful |
| 01_Phones/iPhone 6/iPhone6PlusMockup_v2.psd | 4622×3107 | 1: 0.563 persp. | faithful · filter not redone: Add Noise |
| 01_Phones/iPhone 6/iPhone6PlusMockup_v3.psd | 3648×3648 | 1: 0.563 persp. | faithful · filter not redone: Add Noise |
| 01_Phones/iPhone 6/iPhone6PlusMockup_v4.psd | 3648×3648 | 1: 0.563 persp. | faithful · filter not redone: Add Noise |
| 01_Phones/iPhone5_Photorealistic/1.psd | 5000×3338 | 1: 0.562 persp. | faithful |
| 01_Phones/iPhone5_Photorealistic/2.psd | 5000×3338 | 1: 0.562 persp. | faithful |
| 01_Phones/iPhone5_Photorealistic/3.psd | 5000×3338 | 1: 0.562 persp. | faithful |
| 01_Phones/iPhone5_Photorealistic/4.psd | 5000×3338 | 1: 0.562 persp. | faithful |
| 01_Phones/iPhone5_Photorealistic/5.psd | 5000×3338 | 1: 0.562 persp. | faithful |
| 01_Phones/iPhone5_Photorealistic/6.psd | 5000×3338 | 1: 0.562 persp. | faithful |
| 01_Phones/iphone-mockup-okorkmaz.psd | 3000×2000 | 1: 0.561 persp. | **curated: `phone-app`** · faithful |
| 02_Computers/App-Landing-Page-Template-Free-PSD.psd | 1920×9596 | 0: none | a web page layout, not a mockup |
| 02_Computers/Black_Mockups_for_Sketch_and_Photoshop/Photoshop/Macbook.psd | 1920×1080 | 1: 1.6 | faithful |
| 02_Computers/Black_Mockups_for_Sketch_and_Photoshop/Photoshop/Watch.psd | 1920×1080 | 1: 0.8 curved persp. | faithful |
| 02_Computers/Black_Mockups_for_Sketch_and_Photoshop/Photoshop/iMac.psd | 1920×1080 | 1: 1.778 persp. | faithful |
| 02_Computers/Black_Mockups_for_Sketch_and_Photoshop/Photoshop/iMac_2.psd | 1920×1080 | 2: 1.778 curved persp., 1.778 persp. | faithful |
| 02_Computers/Black_Mockups_for_Sketch_and_Photoshop/Photoshop/iPad.psd.psd | 1920×1080 | 1: 1.333 persp. | faithful |
| 02_Computers/Black_Mockups_for_Sketch_and_Photoshop/Photoshop/iPhone_1.psd | 1920×1080 | 1: 0.562 persp. | faithful |
| 02_Computers/Black_Mockups_for_Sketch_and_Photoshop/Photoshop/iPhone_2.psd | 1920×1080 | 1: 0.562 persp. | faithful |
| 02_Computers/Black_Mockups_for_Sketch_and_Photoshop/Photoshop/iPhone_3.psd | 1920×1080 | 3: 0.562 persp., 0.562 persp., 0.562 persp. | close |
| 02_Computers/Flat iMac Mockup/Flat iMac Mockup.psd | 3000×2000 | 1: 1.6 | renders differently from Photoshop (layer styles) |
| 02_Computers/MacBook Pro Retina.psd | 3000×2051 | 1: 1.6 persp. | **curated: `laptop-website`** · faithful |
| 02_Computers/Macbook Pro.psd | 2000×1500 | 5: 1.111, 1.438, 8.594, 41.457, 52.861 | the device itself is built from smart objects with noise filters; renders differently |
| 02_Computers/iMac.psd | 3454×3454 | 1: 1.778 persp. | screen uses a Blur Gallery filter that isn't reproduced |
| 02_Computers/responsive_website/responsive-showcase-mockup.psd | 2300×1200 | 8: 0.485, 0.563, 0.75, 0.736, 1.829, 1.22, 1.6, 1.752 | faithful · filter not redone: Reduce Noise |
| 03_Tablets/Ipad Retina Display/iPad-Landscape-Retina-Display-Mockup.psd | 6000×3000 | 2: 1.333, 1.333 | renders differently from Photoshop |
| 03_Tablets/Ipad Retina Display/iPad-Retina-Display-Mockup.psd | 5400×3500 | 2: 0.75, 0.75 | renders differently from Photoshop |
| 04_print products/3 Poster Mockup PSD Template.psd | 3000×2000 | 4: 0.17, 0.705, 0.705, 0.705 | faithful |
| 04_print products/A4-CV/A4-Mockup-for-cv.psd | 3600×2500 | 1: 0.707 curved | faithful · filter not redone: Add Noise |
| 04_print products/A4-Landscape-Magazine-Mockup-vol2-PIXEDEN/A4-Landscape-Magazine-Mockup-vol2.psd | 6585×4293 | 3: 1.412 curved persp., 1.415 curved persp., 1.415 curved persp. | renders differently from Photoshop |
| 04_print products/A4-Mockup.psd | 5000×3750 | 1: 0.71 | faithful |
| 04_print products/A4_paper_vertical.psd | 5184×3456 | 1: 0.707 curved persp. | renders differently from Photoshop |
| 04_print products/A5 Magazine on a Grey Surface Mockup.psdt | 5000×3333 | 1: 0.691 persp. | faithful |
| 04_print products/Book-magazine/book_magazine_mockup_free_by_viscondesign.psd | 1900×1351 | 1: 0.706 persp. | faithful |
| 04_print products/Brochure_Square/Square_Brochure_Mockup_1.psd | 2500×1600 | 1: 1.0 curved persp. | faithful |
| 04_print products/Brochure_Square/Square_Brochure_Mockup_2.psd | 2500×1600 | 1: 1.0 curved persp. | faithful |
| 04_print products/Brochure_Square/Square_Brochure_Mockup_3.psd | 2500×1600 | 2: 1.0 curved persp., 1.0 curved persp. | faithful |
| 04_print products/Brochure_Square/Square_Brochure_Mockup_4.psd | 2500×1600 | 2: 1.0 curved persp., 1.0 curved persp. | faithful |
| 04_print products/Brochure_Square/Square_Brochure_Mockup_5.psd | 2500×1600 | 2: 0.953 curved persp., 1.0 curved persp. | faithful |
| 04_print products/Business card/Free_3,5x2in_Business_Card_Mockup_1.psd | 3000×2250 | 2: 1.75 persp., 1.337 | faithful |
| 04_print products/Business card/Free_3,5x2in_Business_Card_Mockup_2.psd | 3000×2250 | 2: 1.75 persp., 1.337 | faithful |
| 04_print products/Business card/Free_3,5x2in_Business_Card_Mockup_3.psd | 3000×2250 | 1: 1.75 persp. | **curated: `business-card-us`** · faithful |
| 04_print products/Business card/Free_3,5x2in_Business_Card_Mockup_4.psd | 3000×2250 | 1: 1.75 persp. | faithful |
| 04_print products/Business card/Free_3,5x2in_Business_Card_Mockup_5.psd | 3000×2250 | 1: 1.75 persp. | faithful |
| 04_print products/Business card/MD317_Free_3,5x2in_Business_Card_Mockup/Free_3,5x2in_Business_Card_Mockup_1.psd | 3000×2250 | 1: 1.75 persp. | faithful |
| 04_print products/Business card/MD317_Free_3,5x2in_Business_Card_Mockup/Free_3,5x2in_Business_Card_Mockup_2.psd | 3000×2250 | 2: 1.75 persp., 1.75 persp. | faithful |
| 04_print products/Business card/MD317_Free_3,5x2in_Business_Card_Mockup/Free_3,5x2in_Business_Card_Mockup_3.psd | 3000×2250 | 2: 1.75 persp., 1.75 persp. | faithful |
| 04_print products/Business card/MD317_Free_3,5x2in_Business_Card_Mockup/Free_3,5x2in_Business_Card_Mockup_4.psd | 3000×2250 | 2: 1.75 persp., 1.75 persp. | faithful |
| 04_print products/Business card/MD317_Free_3,5x2in_Business_Card_Mockup/Free_3,5x2in_Business_Card_Mockup_5.psd | 3000×2250 | 2: 1.75 persp., 1.75 persp. | **curated: `business-cards-us-front-back`** · faithful |
| 04_print products/Business card/MD317_Free_3,5x2in_Business_Card_Mockup/Free_3,5x2in_Business_Card_Mockup_6.psd | 3000×2250 | 2: 1.75 curved persp., 1.75 curved persp. | faithful |
| 04_print products/Business card/MD317_Free_3,5x2in_Business_Card_Mockup/Free_3,5x2in_Business_Card_Mockup_7.psd | 3000×2250 | 2: 1.75 curved persp., 1.75 curved persp. | faithful |
| 04_print products/Essential-Stationery-Mockup.psd | 4600×3600 | 4: 1.415, 0.705, 1.75 persp., 0.709 | renders differently from Photoshop; slow (50 s) |
| 04_print products/Flyer a4-a5/a4-a5-flyer-mockup-02.psd | 3090×3112 | 1: 0.707 | **curated: `a4-page`** · faithful |
| 04_print products/Flyers/Flyer Poster.psd | 2206×1518 | 2: 0.707 persp., 0.707 curved persp. | faithful |
| 04_print products/Lanyard_Mockup/Lanyard_Mockup_1.psd | 2500×1600 | 1: 6.757 curved persp. | faithful |
| 04_print products/Lanyard_Mockup/Lanyard_Mockup_2.psd | 2500×1000 | 1: 6.757 curved persp. | faithful |
| 04_print products/Magazine mockup 2017/01 Cover.psdt | 3201×2000 | 2: 0.707 persp., 0.707 persp. | faithful |
| 04_print products/Magazine mockup 2017/02 Front.psdt | 3201×2000 | 1: 0.707 | faithful |
| 04_print products/Magazine mockup 2017/03 Spread.psdt | 3201×2000 | 4: 0.707 curved, 0.707, 0.707 curved, 0.707 | faithful |
| 04_print products/Magazine mockup 2017/04 Back.psdt | 3201×2000 | 1: 0.707 | faithful |
| 04_print products/Magazine-USLetter-A4-Mockup-Template-PIXEDEN/Magazine-USLetter-A4-Mockup-Template.psd | 6800×5600 | 3: 0.707 curved, 0.7 curved, 0.7 curved | renders differently from Photoshop |
| 04_print products/Magazine-papersize/Back Cover Update.psd | 4801×3599 | 1: 0.707 curved persp. | faithful |
| 04_print products/Magazine-papersize/Front Cover Update.psd | 4801×3599 | 3: 0.707 persp., 0.707 persp., 0.707 persp. | faithful |
| 04_print products/Magazine-papersize/Perspective Spread Update.psd | 4801×3599 | 2: 0.707 curved persp., 0.707 curved persp. | close |
| 04_print products/Magazine-papersize/Spread Update.psd | 4801×3599 | 2: 0.707 curved, 0.707 curved | **curated: `magazine-a4-spread`** · faithful |
| 04_print products/Magazine-papersize/Stack Update.psd | 4801×3599 | 1: 0.707 curved persp. | **curated: `magazine-a4-perspective`** · faithful |
| 04_print products/Magazine/Magazine Mock-up/1.psd | 3000×2200 | 1: 0.751 persp. | faithful |
| 04_print products/Magazine/Magazine Mock-up/2.psd | 3000×2200 | 2: 0.707 curved persp., 0.707 curved persp. | faithful |
| 04_print products/Magazine/Magazine Mock-up/3.psd | 3000×2200 | 2: 0.707 curved persp., 0.707 curved persp. | faithful |
| 04_print products/Magazine/Magazine Mock-up/4.psd | 3000×2200 | 2: 0.707 curved, 0.707 curved | faithful |
| 04_print products/Magazine/Magazine Mock-up/5.psd | 3000×2200 | 2: 0.707 curved persp., 0.707 curved persp. | faithful |
| 04_print products/Magazine/Magazine Mock-up/6.psd | 3000×2200 | 2: 0.714 curved persp., 0.758 curved persp. | faithful |
| 04_print products/Magazine/Magazine Mock-up/7.psd | 3000×2400 | 2: 0.713 curved persp., 0.751 curved | faithful |
| 04_print products/Magazine_A4_front_flat/Magazine_A4_front_flat.psd | 2436×2854 | 1: 0.71 | **curated: `magazine-a4-flat`** · faithful |
| 04_print products/Photorealistic Magazine/Annual Report1/Photorealistic Magazine MockUp 2 copia.psd | 3000×2100 | 3: 0.774 curved persp., 0.774 curved persp., 0.774 curved persp. | renders differently from Photoshop |
| 04_print products/Photorealistic Magazine/Photorealistic Magazine MockUp 2.psd | 3000×2100 | 3: 0.774 curved persp., 0.774 curved persp., 0.774 curved persp. | saved without a preview, so it can't be checked |
| 04_print products/Photorealistic Outdoor Signboard Mockup/outdoor-signboard-mockup.psd | 6000×4800 | 1: 0.681 | faithful · filter not redone: Add Noise |
| 04_print products/Postcard.psd | 4000×2660 | 2: 0.709 curved persp., 0.709 curved persp. | faithful |
| 04_print products/Poster_Set/Mock-up_Poster_horizontal.psd | 2700×2000 | 1: 1.415 curved | **curated: `poster-a-landscape`** · faithful |
| 04_print products/Poster_Set/Mock-up_Poster_square.psd | 2700×2000 | 1: 1.0 curved | **curated: `poster-square`** · faithful |
| 04_print products/Poster_Set/Mock-up_Poster_vertical.psd | 2700×3271 | 1: 0.707 curved | **curated: `poster-a-portrait`** · faithful |
| 04_print products/Rollup - Multiple versions/banners_multiple_versions.psd | 1000×750 | 3: 0.425 persp., 0.425, 0.425 persp. | faithful |
| 04_print products/Rollup Banner/Mockup_Rollup_front_100x200.psd | 1600×2500 | 1: 0.499 persp. | **curated: `rollup-100x200`** · faithful |
| 04_print products/Rollup Banner/Mockup_Rollup_front_120x200.psd | 1600×2500 | 1: 0.6 persp. | faithful |
| 04_print products/Rollup Banner/Mockup_Rollup_front_85x200.psd | 1600×2500 | 1: 0.425 persp. | **curated: `rollup-85x200`** · faithful |
| 04_print products/Rollup Banner/Mockup_Rollup_side_100x200 copy.psd | 4201×3664 | 1: 0.499 persp. | faithful |
| 04_print products/Rollup Banner/Mockup_Rollup_side_100x200.psd | 4201×3664 | 1: 0.499 persp. | faithful |
| 04_print products/Rollup Banner/Mockup_Rollup_side_120x200.psd | 1600×2500 | 1: 0.6 persp. | faithful |
| 04_print products/Rollup Banner/Mockup_Rollup_side_85x200.psd | 1600×2500 | 1: 0.425 persp. | faithful |
| 04_print products/Social Media Jumbo Kit Sample/Sample/Instagram_1.psd | 1080×1080 | 4: 0.632, 1.298, 1.334, 0.71 | faithful |
| 04_print products/Social Media Jumbo Kit Sample/Sample/Instagram_2.psd | 1080×1080 | 1: 0.661 | faithful |
| 04_print products/Social Media Jumbo Kit Sample/Sample/Instagram_3.psd | 1080×1080 | 1: 0.999 | faithful |
| 04_print products/Social Media Jumbo Kit Sample/Sample/Instagram_4.psd | 1080×1080 | 0: none | social post template, no smart object |
| 04_print products/Social Media Jumbo Kit Sample/Sample/Instagram_5.psd | 1080×1080 | 1: 1.0 | faithful |
| 04_print products/a4_simple_mockup.psdt | 4050×2700 | 1: 1.5 | works; colours slightly warmer than Photoshop, paper grain filter not redone; 30 s |
| 04_print products/free_perspectives_business-visiting-cards_mockup-hashnode/perspectives_business-visiting-cards_free-mockup-hashnode.psd | 3600×2700 | 9: 0.92, 1.748 persp., 1.748 persp., 1.75 persp., 1.748 curved persp., 1.748 persp., 1.748 persp., 1.748 persp., 1.748 persp. | faithful |
| 04_print products/mockup.psd | 4000×3000 | 1: 0.707 persp. | close |
| 04_print products/poster_with_clip.psd | 3500×4814 | 2: 0.753, 0.753 | faithful |
| 05_Showcases/AppStarter Sample/Photoshop/AppStarter Sample (Wireframe).psd | 1440×7520 | 8: 1.0 curved, 5.25 curved, 4.05 curved, 5.8 curved, 1.0 curved, 6.0 curved, 7.0 curved, 5.8 curved | a web page layout, not a mockup |
| 05_Showcases/AppStarter Sample/Photoshop/AppStarter Sample.psd | 1440×10586 | 0: none | a web page layout, not a mockup |

Slot shapes are width ÷ height: 0.707 A-series portrait, 1.414 landscape, 1.75 US business
card, 0.562 phone screen, 1.6 laptop screen. No European 85×55 mm (1.55) business-card template
exists in the library.
