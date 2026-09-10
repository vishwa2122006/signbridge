// UI text in Tamil and English. The language toggle picks "ta", "en" or "both";
// in JSX use <T k="key" /> (components/Bilingual.jsx), which stacks Tamil over
// English for "both". t() returns a plain string for attributes and dialogs.
export const STRINGS = {
  tagline: {
    en: "Sign language to Tamil and English text.",
    ta: "சைகை மொழியிலிருந்து தமிழ் மற்றும் ஆங்கில உரை.",
  },
  footer: {
    en: "Communication aid - not a certified interpreter and not medical advice.",
    ta: "தொடர்பு உதவி மட்டுமே - சான்றளிக்கப்பட்ட மொழிபெயர்ப்பாளரோ மருத்துவ ஆலோசனையோ அல்ல.",
  },

  navHome: { en: "Home", ta: "முகப்பு" },
  navTranslate: { en: "Translate", ta: "மொழிபெயர்" },
  navTeach: { en: "Teach Signs", ta: "சைகைகளைக் கற்பி" },
  navConversation: { en: "Conversation", ta: "உரையாடல்" },
  navVocabulary: { en: "Vocabulary", ta: "சொல்லகராதி" },

  // Home
  heroBadge: { en: "Live sign language translation", ta: "நேரடி சைகை மொழிபெயர்ப்பு" },
  homeTitle: {
    en: "Sign in front of your camera. Read it in Tamil and English.",
    ta: "கேமரா முன் சைகை செய்யுங்கள். தமிழிலும் ஆங்கிலத்திலும் படியுங்கள்.",
  },
  homeBody: {
    en: "SignBridge learns the signs you teach it, then turns live signing into Tamil and English text and speech.",
    ta: "நீங்கள் கற்பிக்கும் சைகைகளை SignBridge கற்றுக்கொண்டு, நேரடி சைகைகளைத் தமிழ் மற்றும் ஆங்கில உரையாகவும் பேச்சாகவும் மாற்றுகிறது.",
  },
  startTranslating: { en: "Start translating", ta: "மொழிபெயர்க்கத் தொடங்கு" },
  step1Title: { en: "Teach", ta: "கற்பி" },
  step1Body: {
    en: "Record a few samples of each word and train the model.",
    ta: "ஒவ்வொரு சொல்லுக்கும் சில மாதிரிகளைப் பதிவுசெய்து மாதிரிக்குப் பயிற்சி அளியுங்கள்.",
  },
  step2Title: { en: "Translate", ta: "மொழிபெயர்" },
  step2Body: {
    en: "Sign live - words and sentences appear in Tamil and English.",
    ta: "நேரடியாகச் சைகை செய்யுங்கள் - சொற்களும் வாக்கியங்களும் தமிழிலும் ஆங்கிலத்திலும் தோன்றும்.",
  },
  step3Title: { en: "Converse", ta: "உரையாடு" },
  step3Body: {
    en: "Two-way conversation: your signs become text, replies come back as bilingual phrases.",
    ta: "இருவழி உரையாடல்: உங்கள் சைகைகள் உரையாகின்றன, பதில்கள் இருமொழி சொற்றொடர்களாக வருகின்றன.",
  },
  privacyNote: {
    en: "Video never leaves your device - only hand points are used.",
    ta: "வீடியோ உங்கள் சாதனத்தை விட்டு வெளியேறாது - கை புள்ளிகள் மட்டுமே பயன்படும்.",
  },
  offlineNote: {
    en: "Sentences are formed offline with Tamil grammar rules.",
    ta: "வாக்கியங்கள் தமிழ் இலக்கண விதிகளுடன் இணையமின்றி உருவாகின்றன.",
  },
  customNote: {
    en: "Add your own words with Tamil and English text.",
    ta: "தமிழ் மற்றும் ஆங்கில உரையுடன் உங்கள் சொந்த சொற்களைச் சேர்க்கலாம்.",
  },

  // Camera
  startCamera: { en: "Start camera", ta: "கேமராவைத் தொடங்கு" },
  stopCamera: { en: "Stop camera", ta: "கேமராவை நிறுத்து" },
  cameraOff: { en: "Camera is off.", ta: "கேமரா அணைக்கப்பட்டுள்ளது." },
  cameraLoading: { en: "Loading camera and hand tracking...", ta: "கேமரா மற்றும் கை கண்காணிப்பு ஏற்றப்படுகிறது..." },
  cameraError: { en: "Camera error", ta: "கேமரா பிழை" },
  cameraNotReady: {
    en: "The camera isn't ready yet - wait until you see the video, then record again.",
    ta: "கேமரா இன்னும் தயாராகவில்லை - வீடியோ தெரியும் வரை காத்திருந்து மீண்டும் பதிவு செய்யுங்கள்.",
  },
  live: { en: "LIVE", ta: "நேரலை" },
  backendOffline: {
    en: "Can't reach the backend - start it with: uvicorn app.main:app --port 8000",
    ta: "பின்தள சேவையை அணுக முடியவில்லை - uvicorn app.main:app --port 8000 மூலம் தொடங்கவும்",
  },

  // Translate
  noModelTitle: { en: "No trained model yet", ta: "இன்னும் பயிற்சி பெற்ற மாதிரி இல்லை" },
  noModelBody: {
    en: "Teach the app your signs first: record a few samples of each word, then click Train.",
    ta: "முதலில் உங்கள் சைகைகளைக் கற்பியுங்கள்: ஒவ்வொரு சொல்லுக்கும் சில மாதிரிகளைப் பதிவுசெய்து, பயிற்சி அளிக்கவும்.",
  },
  goTeach: { en: "Go to Teach Signs", ta: "சைகைகளைக் கற்பி பக்கத்திற்குச் செல்" },
  wordsKnown: { en: "words the model knows", ta: "மாதிரிக்குத் தெரிந்த சொற்கள்" },
  confidence: { en: "Confidence", ta: "நம்பகத்தன்மை" },
  reset: { en: "Reset", ta: "மீட்டமை" },
  waitingForCamera: { en: "Start the camera and sign a word.", ta: "கேமராவைத் தொடங்கி ஒரு சொல்லைச் சைகை செய்யுங்கள்." },
  patientSigning: { en: "Emergency sign:", ta: "அவசர சைகை:" },
  emergencyAlertTitle: { en: "COMMUNICATION ALERT", ta: "தொடர்பு எச்சரிக்கை" },

  // Sentence builder
  signedWords: { en: "Signed words", ta: "சைகை சொற்கள்" },
  noWordsYet: { en: "Recognized words will appear here.", ta: "அடையாளம் காணப்பட்ட சொற்கள் இங்கே தோன்றும்." },
  undo: { en: "Undo", ta: "பின்செல்" },
  clear: { en: "Clear", ta: "அழி" },
  speak: { en: "Speak", ta: "பேசு" },
  send: { en: "Send", ta: "அனுப்பு" },

  // Teach
  teachIntro: {
    en: "Pick a word, press Record and perform the sign when the countdown ends. Only hand and body points are saved - never video.",
    ta: "ஒரு சொல்லைத் தேர்ந்தெடுத்து, பதிவு பொத்தானை அழுத்தி, எண்ணிக்கை முடிந்ததும் சைகையைச் செய்யுங்கள். கை மற்றும் உடல் புள்ளிகள் மட்டுமே சேமிக்கப்படும் - வீடியோ ஒருபோதும் சேமிக்கப்படாது.",
  },
  signerName: { en: "Signer name", ta: "சைகை செய்பவர் பெயர்" },
  searchWords: { en: "Search words...", ta: "சொற்களைத் தேடு..." },
  allCategories: { en: "All categories", ta: "அனைத்து பிரிவுகளும்" },
  idleSign: { en: "Idle (no sign)", ta: "ஓய்வு (சைகை இல்லை)" },
  idleHelp: {
    en: "Record your hands resting or moving without signing, so the translator knows when you are not signing.",
    ta: "சைகை செய்யாமல் கைகளை ஓய்வாக அல்லது இயல்பாக அசைப்பதைப் பதிவுசெய்யுங்கள் - நீங்கள் சைகை செய்யாதபோது மொழிபெயர்ப்பாளருக்குத் தெரியும்.",
  },
  recordOne: { en: "Record 1", ta: "1 பதிவு" },
  recordTen: { en: "Record 10", ta: "10 பதிவுகள்" },
  stop: { en: "Stop", ta: "நிறுத்து" },
  getReady: { en: "Get ready", ta: "தயாராகுங்கள்" },
  recording: { en: "Sign now!", ta: "இப்போது சைகை செய்யுங்கள்!" },
  saved: { en: "Saved", ta: "சேமிக்கப்பட்டது" },
  wordAdded: { en: "Word added", ta: "சொல் சேர்க்கப்பட்டது" },
  selectWordFirst: { en: "Select a word to record.", ta: "பதிவு செய்ய ஒரு சொல்லைத் தேர்ந்தெடுக்கவும்." },
  enterSignerName: { en: "Enter the signer's name first.", ta: "முதலில் சைகை செய்பவரின் பெயரை உள்ளிடவும்." },
  noHandsInRecording: {
    en: "Hands weren't visible in most of this recording - keep your hands inside the camera view.",
    ta: "இந்தப் பதிவில் பெரும்பாலும் கைகள் தெரியவில்லை - கைகளை கேமரா பார்வைக்குள் வைத்திருங்கள்.",
  },
  samples: { en: "Samples", ta: "மாதிரிகள்" },
  signers: { en: "Signers", ta: "சைகையாளர்கள்" },
  samplesSigners: { en: "Samples / signers", ta: "மாதிரிகள் / சைகையாளர்கள்" },
  deleteLast: { en: "Delete last", ta: "கடைசியை நீக்கு" },
  recordedWords: { en: "Recorded", ta: "பதிவுசெய்யப்பட்டவை" },
  nothingRecorded: { en: "Nothing recorded yet.", ta: "இன்னும் எதுவும் பதிவு செய்யப்படவில்லை." },
  train: { en: "Train model", ta: "மாதிரிக்குப் பயிற்சி அளி" },
  training: { en: "Training...", ta: "பயிற்சி நடக்கிறது..." },
  trainingBusy: { en: "Training is already running - please wait.", ta: "பயிற்சி ஏற்கனவே நடக்கிறது - காத்திருக்கவும்." },
  trainHint: {
    en: "For good results: 15+ samples per word, from 2 or more people, in different positions and lighting - plus Idle samples.",
    ta: "நல்ல முடிவுகளுக்கு: ஒரு சொல்லுக்கு 15+ மாதிரிகள், 2 அல்லது அதற்கு மேற்பட்டவர்களிடமிருந்து, வெவ்வேறு நிலைகள் மற்றும் வெளிச்சத்தில் - ஓய்வு மாதிரிகளுடன்.",
  },
  notEnoughData: {
    en: "Not enough recordings to train yet. Record at least {min} samples for at least 2 signs (Idle counts as one).",
    ta: "பயிற்சி அளிக்க இன்னும் போதுமான பதிவுகள் இல்லை. குறைந்தது 2 சைகைகளுக்கு, ஒவ்வொன்றுக்கும் குறைந்தது {min} மாதிரிகளைப் பதிவு செய்யுங்கள் (ஓய்வும் ஒன்றாகக் கணக்கிடப்படும்).",
  },
  warnFewSigners: {
    en: "Only {n} signer(s): accuracy was measured on the same people, so expect lower accuracy for new signers. Record 3+ people for an honest number.",
    ta: "{n} சைகையாளர்(கள்) மட்டுமே: அதே நபர்களிடம் துல்லியம் அளவிடப்பட்டது, புதியவர்களுக்குக் குறைவாக இருக்கலாம். சரியான அளவுக்கு 3+ நபர்களைப் பதிவு செய்யுங்கள்.",
  },
  warnNoIdle: {
    en: "No Idle samples: record some so the translator stays quiet while your hands rest.",
    ta: "ஓய்வு மாதிரிகள் இல்லை: கைகள் ஓய்வில் இருக்கும்போது மொழிபெயர்ப்பாளர் அமைதியாக இருக்க சிலவற்றைப் பதிவு செய்யுங்கள்.",
  },
  warnSkipped: {
    en: "Not trained yet (fewer than {min} samples):",
    ta: "இன்னும் பயிற்சி பெறவில்லை ({min} மாதிரிகளுக்குக் குறைவு):",
  },
  warnNoCv: {
    en: "Not enough samples to measure accuracy yet.",
    ta: "துல்லியத்தை அளவிட இன்னும் போதுமான மாதிரிகள் இல்லை.",
  },
  lastTraining: { en: "Last training", ta: "கடைசி பயிற்சி" },
  cvAccuracy: { en: "Accuracy", ta: "துல்லியம்" },
  cvSignerHeldOut: { en: "tested on unseen signers", ta: "புதிய சைகையாளர்களிடம் சோதிக்கப்பட்டது" },
  cvStratified: { en: "tested on the same signers", ta: "அதே சைகையாளர்களிடம் சோதிக்கப்பட்டது" },
  acceptedRate: { en: "Answered confidently", ta: "நம்பிக்கையுடன் பதிலளித்தவை" },
  precisionAtThreshold: { en: "Correct when confident", ta: "நம்பிக்கையுடன் சரியானவை" },
  word: { en: "Word", ta: "சொல்" },
  addWord: { en: "Add a new word", ta: "புதிய சொல்லைச் சேர்" },
  english: { en: "English", ta: "ஆங்கிலம்" },
  tamil: { en: "Tamil", ta: "தமிழ்" },
  category: { en: "Category", ta: "பிரிவு" },
  emergencyWord: { en: "Emergency word", ta: "அவசர சொல்" },
  add: { en: "Add", ta: "சேர்" },

  // Conversation
  patient: { en: "Signer", ta: "சைகை செய்பவர்" },
  staff: { en: "Hearing person", ta: "கேட்கும் நபர்" },
  pickWordsManually: { en: "Can't sign it? Pick words instead", ta: "சைகை செய்ய முடியவில்லையா? சொற்களைத் தேர்ந்தெடுங்கள்" },
  quickPhrases: { en: "Quick phrases (sent in both languages)", ta: "விரைவு சொற்றொடர்கள் (இரு மொழிகளிலும் அனுப்பப்படும்)" },
  quickReplies: { en: "Quick replies", ta: "விரைவு பதில்கள்" },
  typeOrDictate: { en: "Or type / dictate a message", ta: "அல்லது செய்தியைத் தட்டச்சு செய்யவும் / பேசவும்" },
  typeHere: { en: "Type a message...", ta: "செய்தியைத் தட்டச்சு செய்யவும்..." },
  typeShort: { en: "Type...", ta: "தட்டச்சு..." },
  dictate: { en: "Dictate", ta: "குரல் பதிவு" },
  listening: { en: "Listening...", ta: "கேட்கிறது..." },
  conversationLog: { en: "Conversation", ta: "உரையாடல்" },
  conversationEmpty: {
    en: "Messages from both sides appear here - the newest is always at the bottom.",
    ta: "இரு பக்கச் செய்திகளும் இங்கே தோன்றும் - புதியது எப்போதும் கீழே இருக்கும்.",
  },
  latest: { en: "Latest", ta: "சமீபத்தியது" },
  untranslated: { en: "typed text - not translated", ta: "தட்டச்சு உரை - மொழிபெயர்க்கப்படவில்லை" },
  inSigns: { en: "In signs", ta: "சைகையில்" },
  showSigns: { en: "Show in signs", ta: "சைகையில் காட்டு" },
  hideSigns: { en: "Hide signs", ta: "சைகையை மறை" },
  loadingSigns: { en: "Finding signs...", ta: "சைகைகளைத் தேடுகிறது..." },
  replay: { en: "Replay", ta: "மீண்டும்" },
  slow: { en: "Slow", ta: "மெதுவாக" },
  notSigned: { en: "no recorded sign for this word", ta: "இந்தச் சொல்லுக்குப் பதிவுசெய்த சைகை இல்லை" },
  noSignsRecorded: {
    en: "No recorded signs for these words yet - record them on Teach Signs.",
    ta: "இந்தச் சொற்களுக்கு இன்னும் பதிவுசெய்த சைகைகள் இல்லை - 'சைகைகளைக் கற்பி' பக்கத்தில் பதிவு செய்யுங்கள்.",
  },
  signsFromRecordings: {
    en: "Replayed from recordings made on Teach Signs",
    ta: "'சைகைகளைக் கற்பி' பதிவுகளிலிருந்து காட்டப்படுகிறது",
  },
  noSpeechRecognition: {
    en: "This browser doesn't support speech recognition.",
    ta: "இந்த உலாவி பேச்சு அறிதலை ஆதரிக்கவில்லை.",
  },

  // Vocabulary
  vocabIntro: {
    en: "Every word the app can learn. Record a word on the Teach Signs page and train to make it recognizable.",
    ta: "செயலி கற்றுக்கொள்ளக்கூடிய அனைத்து சொற்களும். ஒரு சொல்லை அடையாளம் காண, 'சைகைகளைக் கற்பி' பக்கத்தில் பதிவுசெய்து பயிற்சி அளிக்கவும்.",
  },
  totalWords: { en: "Words", ta: "சொற்கள்" },
  customWords: { en: "Custom words", ta: "தனிப்பயன் சொற்கள்" },
  totalSamples: { en: "Recorded samples", ta: "பதிவு மாதிரிகள்" },
  status: { en: "Status", ta: "நிலை" },
  trained: { en: "Trained", ta: "பயிற்சி பெற்றது" },
  notTrained: { en: "Not trained", ta: "பயிற்சி இல்லை" },
  custom: { en: "custom", ta: "தனிப்பயன்" },
  delete: { en: "Delete", ta: "நீக்கு" },
  confirmDeleteWord: {
    en: "Delete this word and all its recorded samples?",
    ta: "இந்த சொல்லையும் அதன் அனைத்து மாதிரிகளையும் நீக்கவா?",
  },
};

export function format(text, vars) {
  if (!vars) return text;
  return text.replace(/\{(\w+)\}/g, (match, name) => (name in vars ? String(vars[name]) : match));
}

/** Plain-string version of a UI text for attributes, placeholders and dialogs. */
export function t(key, lang, vars) {
  const entry = STRINGS[key];
  if (!entry) return key;
  if (lang === "en") return format(entry.en, vars);
  if (lang === "ta") return format(entry.ta, vars);
  return `${format(entry.ta, vars)} / ${format(entry.en, vars)}`;
}

/** Plain-string Tamil and/or English for a bilingual record ({ tamil, english }). */
export function pickText({ tamil, english }, lang) {
  if (lang === "en") return english;
  if (lang === "ta") return tamil;
  return `${tamil} / ${english}`;
}
