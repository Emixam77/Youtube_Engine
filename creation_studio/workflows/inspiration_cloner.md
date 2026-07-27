# 🔄 WORKFLOW : INSPIRATION CLONER (Reverse Engineering)

Ce workflow permet d'analyser une vidéo d'inspiration (URL YouTube/TikTok/Reels ou transcription) et d'en extraire la substantifique moelle pour créer une version originale et sublimée dans le format souhaité (Short 9:16 ou HD 16:9).

---

## 🔍 Étape 1 : Ingestion & Analyse de la Source
1. **Extraction de la transcription** : Si une URL est fournie, utiliser `yt-dlp` pour récupérer le script exact ou les sous-titres.
2. **Audit de la Structure (Deconstruction)** :
   - **Hook** : Quel est le levier utilisé ? (Peur, curiosité, statut, statistiques, absurdité)
   - **Rhythm & Cuts** : Fréquence des changements de plan.
   - **Visual Identity** : Style visuel (Collage, 3D, Cinématique, Real-life archive, Motion graphics).
   - **Core Message** : Quelle est l'idée clé à retenir ?

---

## ✍️ Étape 2 : Ré-écriture & Adaptation Créative
1. **Conserver le squelette émotionnel** (ce qui fait marcher la vidéo).
2. **Remplacer 100% de la substance et du texte** par une histoire / sujet totalement originale.
3. **Formater le script** selon le template cible :
   - Pour un Short : charger `creation_studio/templates/short_pipeline.md`
   - Pour une Vidéo HD : charger `creation_studio/templates/hd_video_pipeline.md`

---

## 🎨 Étape 3 : Spécification DA & Prompts Google Flow
1. Définir une **Direction Artistique dédiée** (Color Palette, Texture, Style d'images).
2. Produire la liste des **prompts d'images / B-Rolls** prêts pour le serveur Google Flow avec l'aspect ratio adapté.
3. Produire le script voix off avec indications de rythme pour ElevenLabs.
