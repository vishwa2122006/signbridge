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
  navReview: { en: "Review & Train", ta: "சரிபார்த்து பயிற்சி" },
  navAccount: { en: "My account", ta: "என் கணக்கு" },
  logIn: { en: "Log in", ta: "உள்நுழை" },
  logOut: { en: "Log out", ta: "வெளியேறு" },
  roleAdmin: { en: "Admin", ta: "நிர்வாகி" },
  roleTrainer: { en: "Trainer", ta: "பயிற்சியாளர்" },

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
    en: "Trainers record a few samples of each word; an admin approves them and trains the model.",
    ta: "பயிற்சியாளர்கள் ஒவ்வொரு சொல்லுக்கும் சில மாதிரிகளைப் பதிவு செய்கிறார்கள்; நிர்வாகி அவற்றை ஏற்று மாதிரிக்குப் பயிற்சி அளிக்கிறார்.",
  },
  becomeTrainerTitle: { en: "Become a trainer", ta: "பயிற்சியாளர் ஆகுங்கள்" },
  becomeTrainerBody: {
    en: "Register to record the signs that teach SignBridge. An admin reviews every recording.",
    ta: "SignBridge-க்குக் கற்பிக்கும் சைகைகளைப் பதிவு செய்ய பதிவு செய்யுங்கள். ஒவ்வொரு பதிவையும் நிர்வாகி சரிபார்க்கிறார்.",
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
    en: "The model hasn't been trained yet. Please check back soon.",
    ta: "மாதிரிக்கு இன்னும் பயிற்சி அளிக்கப்படவில்லை. விரைவில் மீண்டும் பாருங்கள்.",
  },
  noModelBodyTrainer: {
    en: "Record signs on Teach Signs and submit them; an admin trains the model once they're approved.",
    ta: "'சைகைகளைக் கற்பி' பக்கத்தில் சைகைகளைப் பதிவுசெய்து சமர்ப்பியுங்கள்; அவை ஏற்கப்பட்டதும் நிர்வாகி மாதிரிக்குப் பயிற்சி அளிப்பார்.",
  },
  noModelBodyAdmin: {
    en: "Approve recordings and train the model on the Review & Train page.",
    ta: "'சரிபார்த்து பயிற்சி' பக்கத்தில் பதிவுகளை ஏற்று மாதிரிக்குப் பயிற்சி அளியுங்கள்.",
  },
  goTeach: { en: "Go to Teach Signs", ta: "சைகைகளைக் கற்பி பக்கத்திற்குச் செல்" },
  goReview: { en: "Go to Review & Train", ta: "சரிபார்த்து பயிற்சி பக்கத்திற்குச் செல்" },
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
  teachIntroTrainer: {
    en: "Pick a word, press Record and perform the sign when the countdown ends. Recordings stay private drafts until you submit them for review. Only hand and body points are saved - never video.",
    ta: "ஒரு சொல்லைத் தேர்ந்தெடுத்து, பதிவு பொத்தானை அழுத்தி, எண்ணிக்கை முடிந்ததும் சைகையைச் செய்யுங்கள். சரிபார்ப்புக்குச் சமர்ப்பிக்கும் வரை பதிவுகள் தனிப்பட்ட வரைவுகளாக இருக்கும். கை மற்றும் உடல் புள்ளிகள் மட்டுமே சேமிக்கப்படும் - வீடியோ ஒருபோதும் சேமிக்கப்படாது.",
  },
  teachIntroAdmin: {
    en: "Pick a word, press Record and perform the sign when the countdown ends. Your recordings are approved straight away. Only hand and body points are saved - never video.",
    ta: "ஒரு சொல்லைத் தேர்ந்தெடுத்து, பதிவு பொத்தானை அழுத்தி, எண்ணிக்கை முடிந்ததும் சைகையைச் செய்யுங்கள். உங்கள் பதிவுகள் உடனே ஏற்கப்படும். கை மற்றும் உடல் புள்ளிகள் மட்டுமே சேமிக்கப்படும் - வீடியோ ஒருபோதும் சேமிக்கப்படாது.",
  },
  recordingAs: { en: "Recording as", ta: "பதிவு செய்பவர்" },
  welcomeTrainer: {
    en: "Welcome! You're a trainer now. Record a word, then submit your recordings for review.",
    ta: "வரவேற்கிறோம்! நீங்கள் இப்போது பயிற்சியாளர். ஒரு சொல்லைப் பதிவுசெய்து, பின் உங்கள் பதிவுகளைச் சரிபார்ப்புக்குச் சமர்ப்பியுங்கள்.",
  },
  searchWords: { en: "Search words...", ta: "சொற்களைத் தேடு..." },
  allCategories: { en: "All categories", ta: "அனைத்து பிரிவுகளும்" },
  idleSign: { en: "Idle (no sign)", ta: "ஓய்வு (சைகை இல்லை)" },
  idleHelp: {
    en: "Record your hands resting or moving without signing, so the translator knows when you are not signing.",
    ta: "சைகை செய்யாமல் கைகளை ஓய்வாக அல்லது இயல்பாக அசைப்பதைப் பதிவுசெய்யுங்கள் - நீங்கள் சைகை செய்யாதபோது மொழிபெயர்ப்பாளருக்குத் தெரியும்.",
  },
  recordOne: { en: "Record 1", ta: "1 பதிவு" },
  recordingLength: { en: "Recording length", ta: "பதிவு நேரம்" },
  lengthMismatch: {
    en: "Other recordings of this word are about {s} long. Use the same length so the translator recognizes it reliably.",
    ta: "இந்தச் சொல்லின் மற்ற பதிவுகள் சுமார் {s} நீளம். மொழிபெயர்ப்பாளர் சரியாக அடையாளம் காண அதே நேர அளவைப் பயன்படுத்தவும்.",
  },
  recordTen: { en: "Record 10", ta: "10 பதிவுகள்" },
  stop: { en: "Stop", ta: "நிறுத்து" },
  getReady: { en: "Get ready", ta: "தயாராகுங்கள்" },
  recording: { en: "Sign now!", ta: "இப்போது சைகை செய்யுங்கள்!" },
  saved: { en: "Saved", ta: "சேமிக்கப்பட்டது" },
  wordAdded: { en: "Word added", ta: "சொல் சேர்க்கப்பட்டது" },
  selectWordFirst: { en: "Select a word to record.", ta: "பதிவு செய்ய ஒரு சொல்லைத் தேர்ந்தெடுக்கவும்." },
  savedDraft: { en: "Saved as draft", ta: "வரைவாகச் சேமிக்கப்பட்டது" },
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
    en: "Not enough approved recordings to train yet. Approve at least {min} recordings for each of at least 2 signs (Idle counts as one).",
    ta: "பயிற்சி அளிக்க இன்னும் போதுமான ஏற்கப்பட்ட பதிவுகள் இல்லை. குறைந்தது 2 சைகைகளுக்கு, ஒவ்வொன்றுக்கும் குறைந்தது {min} பதிவுகளை ஏற்கவும் (ஓய்வும் ஒன்றாகக் கணக்கிடப்படும்).",
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
  warnMixedLengths: {
    en: "Recordings of very different lengths - record each word at one length:",
    ta: "மிகவும் வேறுபட்ட நீளமுள்ள பதிவுகள் - ஒவ்வொரு சொல்லையும் ஒரே நீளத்தில் பதிவு செய்யுங்கள்:",
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
  proposeWord: { en: "Propose a new word", ta: "புதிய சொல்லைப் பரிந்துரை" },
  proposeHint: {
    en: "An admin approves new words before everyone can see them. You can record the word right away.",
    ta: "புதிய சொற்களை அனைவரும் பார்ப்பதற்கு முன் நிர்வாகி ஒப்புதல் அளிக்கிறார். நீங்கள் அந்தச் சொல்லை உடனே பதிவு செய்யலாம்.",
  },
  propose: { en: "Propose", ta: "பரிந்துரை" },
  wordProposed: { en: "Word sent for approval", ta: "சொல் ஒப்புதலுக்கு அனுப்பப்பட்டது" },
  awaitingApproval: { en: "Waiting for admin approval", ta: "நிர்வாகியின் ஒப்புதலுக்குக் காத்திருக்கிறது" },
  myRecordings: { en: "My recordings", ta: "என் பதிவுகள்" },
  submitForReview: { en: "Submit {n} for review", ta: "{n} பதிவுகளைச் சரிபார்ப்புக்குச் சமர்ப்பி" },
  submittedNotice: {
    en: "{n} recordings sent for review. You'll get an email when they're reviewed.",
    ta: "{n} பதிவுகள் சரிபார்ப்புக்கு அனுப்பப்பட்டன. சரிபார்த்ததும் உங்களுக்கு மின்னஞ்சல் வரும்.",
  },
  reviewHint: {
    en: "Drafts are only visible to you. After you submit, an admin approves or rejects each recording; only approved ones train the model.",
    ta: "வரைவுகள் உங்களுக்கு மட்டுமே தெரியும். சமர்ப்பித்த பிறகு, நிர்வாகி ஒவ்வொரு பதிவையும் ஏற்கிறார் அல்லது நிராகரிக்கிறார்; ஏற்கப்பட்டவை மட்டுமே மாதிரிக்குப் பயிற்சி அளிக்கும்.",
  },
  adminRecordHint: {
    en: "Your recordings are approved automatically. Review trainers' recordings and train the model on the Review & Train page.",
    ta: "உங்கள் பதிவுகள் தானாக ஏற்கப்படும். பயிற்சியாளர்களின் பதிவுகளைச் சரிபார்த்து 'சரிபார்த்து பயிற்சி' பக்கத்தில் மாதிரிக்குப் பயிற்சி அளியுங்கள்.",
  },
  goReviewTrain: { en: "Review & train", ta: "சரிபார்த்து பயிற்சி" },
  status_draft: { en: "Draft", ta: "வரைவு" },
  status_pending: { en: "Waiting", ta: "காத்திருப்பு" },
  status_approved: { en: "Approved", ta: "ஏற்கப்பட்டது" },
  status_rejected: { en: "Rejected", ta: "நிராகரிக்கப்பட்டது" },

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
    en: "No recorded signs for these words yet.",
    ta: "இந்தச் சொற்களுக்கு இன்னும் பதிவுசெய்த சைகைகள் இல்லை.",
  },
  signsFromRecordings: {
    en: "Replayed from trainers' approved recordings",
    ta: "பயிற்சியாளர்களின் ஏற்கப்பட்ட பதிவுகளிலிருந்து காட்டப்படுகிறது",
  },
  noSpeechRecognition: {
    en: "This browser doesn't support speech recognition.",
    ta: "இந்த உலாவி பேச்சு அறிதலை ஆதரிக்கவில்லை.",
  },

  // Vocabulary
  vocabIntro: {
    en: "Every word the app can learn. Trainers record the words and an admin trains the model to recognize them.",
    ta: "செயலி கற்றுக்கொள்ளக்கூடிய அனைத்து சொற்களும். பயிற்சியாளர்கள் சொற்களைப் பதிவு செய்கிறார்கள்; அவற்றை அடையாளம் காண நிர்வாகி மாதிரிக்குப் பயிற்சி அளிக்கிறார்.",
  },
  totalWords: { en: "Words", ta: "சொற்கள்" },
  customWords: { en: "Custom words", ta: "தனிப்பயன் சொற்கள்" },
  totalSamples: { en: "Approved recordings", ta: "ஏற்கப்பட்ட பதிவுகள்" },
  status: { en: "Status", ta: "நிலை" },
  trained: { en: "Trained", ta: "பயிற்சி பெற்றது" },
  notTrained: { en: "Not trained", ta: "பயிற்சி இல்லை" },
  custom: { en: "custom", ta: "தனிப்பயன்" },
  delete: { en: "Delete", ta: "நீக்கு" },
  confirmDeleteWord: {
    en: "Delete this word and all its recorded samples?",
    ta: "இந்த சொல்லையும் அதன் அனைத்து மாதிரிகளையும் நீக்கவா?",
  },

  // Login & registration
  loginTitle: { en: "Trainer & admin login", ta: "பயிற்சியாளர் & நிர்வாகி உள்நுழைவு" },
  loginIntro: {
    en: "Trainers record signs for the model; admins review them and train it. Translating and conversation need no login.",
    ta: "பயிற்சியாளர்கள் மாதிரிக்காகச் சைகைகளைப் பதிவு செய்கிறார்கள்; நிர்வாகிகள் அவற்றைச் சரிபார்த்துப் பயிற்சி அளிக்கிறார்கள். மொழிபெயர்ப்புக்கும் உரையாடலுக்கும் உள்நுழைவு தேவையில்லை.",
  },
  withPassword: { en: "Password", ta: "கடவுச்சொல்" },
  withEmailCode: { en: "Email code", ta: "மின்னஞ்சல் குறியீடு" },
  email: { en: "Email", ta: "மின்னஞ்சல்" },
  password: { en: "Password", ta: "கடவுச்சொல்" },
  codeLoginHelp: {
    en: "We'll email you a one-time code - no password needed.",
    ta: "ஒருமுறைக் குறியீட்டை மின்னஞ்சலில் அனுப்புவோம் - கடவுச்சொல் தேவையில்லை.",
  },
  sendCode: { en: "Send code", ta: "குறியீட்டை அனுப்பு" },
  codeSentTo: { en: "We sent a code to", ta: "குறியீடு அனுப்பப்பட்ட மின்னஞ்சல்:" },
  code: { en: "Code", ta: "குறியீடு" },
  verifyCode: { en: "Verify", ta: "சரிபார்" },
  resendCode: { en: "Send a new code", ta: "புதிய குறியீட்டை அனுப்பு" },
  resendIn: { en: "New code in {s}s", ta: "{s} வினாடிகளில் புதிய குறியீடு" },
  codeResent: { en: "A new code is on its way.", ta: "புதிய குறியீடு அனுப்பப்பட்டது." },
  changeEmail: { en: "Change email", ta: "மின்னஞ்சலை மாற்று" },
  newTrainer: { en: "Want to help train SignBridge?", ta: "SignBridge-க்குப் பயிற்சி அளிக்க உதவ விரும்புகிறீர்களா?" },
  registerLink: { en: "Register as a trainer", ta: "பயிற்சியாளராகப் பதிவு செய்யுங்கள்" },
  haveAccount: { en: "Already registered?", ta: "ஏற்கனவே பதிவு செய்துவிட்டீர்களா?" },
  logInLink: { en: "Log in", ta: "உள்நுழையுங்கள்" },
  alreadyLoggedIn: { en: "You're logged in as {name}.", ta: "நீங்கள் {name} ஆக உள்நுழைந்துள்ளீர்கள்." },
  continue: { en: "Continue", ta: "தொடர்" },
  registerTitle: { en: "Become a trainer", ta: "பயிற்சியாளர் ஆகுங்கள்" },
  registerIntro: {
    en: "Trainers record the signs that teach SignBridge, and an admin reviews every recording before it's used. We'll email you a code to confirm your address.",
    ta: "பயிற்சியாளர்கள் பதிவு செய்யும் சைகைகள் SignBridge-க்குக் கற்பிக்கின்றன; ஒவ்வொரு பதிவும் பயன்படுத்தப்படுவதற்கு முன் நிர்வாகி சரிபார்க்கிறார். உங்கள் முகவரியை உறுதிசெய்ய ஒரு குறியீட்டை மின்னஞ்சலில் அனுப்புவோம்.",
  },
  aboutYou: { en: "About you", ta: "உங்களைப் பற்றி" },
  fullName: { en: "Full name", ta: "முழுப் பெயர்" },
  phone: { en: "Phone", ta: "தொலைபேசி" },
  city: { en: "City / town", ta: "நகரம் / ஊர்" },
  organization: { en: "Organization (optional)", ta: "நிறுவனம் (விருப்பத்தேர்வு)" },
  organizationLabel: { en: "Organization", ta: "நிறுவனம்" },
  organizationPlaceholder: { en: "School, hospital, NGO...", ta: "பள்ளி, மருத்துவமனை, தொண்டு நிறுவனம்..." },
  yourSigning: { en: "Your signing", ta: "உங்கள் சைகை அனுபவம்" },
  background: { en: "Background", ta: "பின்னணி" },
  signingLevel: { en: "Signing level", ta: "சைகைத் திறன்" },
  signLanguage: { en: "Sign language you use", ta: "நீங்கள் பயன்படுத்தும் சைகை மொழி" },
  about: { en: "Anything else? (optional)", ta: "வேறு ஏதேனும்? (விருப்பத்தேர்வு)" },
  choose: { en: "Choose...", ta: "தேர்ந்தெடுக்கவும்..." },
  confirmPassword: { en: "Repeat password", ta: "கடவுச்சொல்லை மீண்டும் உள்ளிடவும்" },
  passwordHint: { en: "At least 6 characters.", ta: "குறைந்தது 6 எழுத்துகள்." },
  consentText: {
    en: "I agree that my recordings (hand and body points only, never video) are used to train SignBridge.",
    ta: "எனது பதிவுகள் (கை மற்றும் உடல் புள்ளிகள் மட்டும், வீடியோ அல்ல) SignBridge-க்குப் பயிற்சி அளிக்கப் பயன்படுத்தப்படுவதை ஒப்புக்கொள்கிறேன்.",
  },
  registerAndSendCode: { en: "Register & email me a code", ta: "பதிவு செய்து குறியீட்டை அனுப்பு" },
  passwordsDontMatch: { en: "The passwords don't match.", ta: "கடவுச்சொற்கள் பொருந்தவில்லை." },
  bg_deaf: { en: "Deaf signer", ta: "காது கேளாத சைகையாளர்" },
  bg_hard_of_hearing: { en: "Hard of hearing", ta: "செவித்திறன் குறைந்தவர்" },
  bg_interpreter: { en: "Sign language interpreter", ta: "சைகை மொழிபெயர்ப்பாளர்" },
  bg_teacher: { en: "Teacher of Deaf students", ta: "காது கேளாத மாணவர்களின் ஆசிரியர்" },
  bg_family: { en: "Family or friend of a Deaf person", ta: "காது கேளாதவரின் குடும்பத்தினர் / நண்பர்" },
  bg_student: { en: "Student / learner", ta: "மாணவர் / கற்பவர்" },
  bg_other: { en: "Other", ta: "மற்றவை" },
  level_native: { en: "Native signer", ta: "தாய்மொழிச் சைகையாளர்" },
  level_fluent: { en: "Fluent", ta: "சரளமாக" },
  level_intermediate: { en: "Intermediate", ta: "இடைநிலை" },
  level_beginner: { en: "Beginner", ta: "தொடக்க நிலை" },
  lang_tamil: { en: "Tamil Sign Language", ta: "தமிழ் சைகை மொழி" },
  lang_indian: { en: "Indian Sign Language (ISL)", ta: "இந்திய சைகை மொழி (ISL)" },
  lang_both: { en: "Tamil and Indian Sign Language", ta: "தமிழ் மற்றும் இந்திய சைகை மொழி" },
  lang_other: { en: "Other", ta: "மற்றவை" },

  // Account
  changePassword: { en: "Change password", ta: "கடவுச்சொல்லை மாற்று" },
  changePasswordHint: {
    en: "You can also log in with an email code at any time, so a forgotten password is never a problem.",
    ta: "எப்போது வேண்டுமானாலும் மின்னஞ்சல் குறியீட்டுடன் உள்நுழையலாம் - கடவுச்சொல் மறந்தாலும் பிரச்சினை இல்லை.",
  },
  currentPassword: { en: "Current password", ta: "தற்போதைய கடவுச்சொல்" },
  newPassword: { en: "New password", ta: "புதிய கடவுச்சொல்" },
  passwordChanged: {
    en: "Password changed. Other devices were logged out.",
    ta: "கடவுச்சொல் மாற்றப்பட்டது. மற்ற சாதனங்களிலிருந்து வெளியேற்றப்பட்டது.",
  },
  joined: { en: "Joined", ta: "இணைந்தது" },

  // Review & Train (admins)
  reviewIntro: {
    en: "Watch each trainer's recordings, approve the good ones and reject the rest, then train the model on the approved recordings. Trainers get an email about every decision.",
    ta: "ஒவ்வொரு பயிற்சியாளரின் பதிவுகளையும் பார்த்து, சரியானவற்றை ஏற்று மற்றவற்றை நிராகரியுங்கள்; பின் ஏற்கப்பட்ட பதிவுகளைக் கொண்டு மாதிரிக்குப் பயிற்சி அளியுங்கள். ஒவ்வொரு முடிவும் பயிற்சியாளருக்கு மின்னஞ்சலில் தெரிவிக்கப்படும்.",
  },
  tabRecordings: { en: "Recordings", ta: "பதிவுகள்" },
  tabTrainers: { en: "Trainers", ta: "பயிற்சியாளர்கள்" },
  tabModels: { en: "Models", ta: "மாதிரிகள்" },
  trainedModels: { en: "Trained models", ta: "பயிற்சி பெற்ற மாதிரிகள்" },
  modelsIntro: {
    en: "Every training is kept as a version. The translator uses the one marked In use: switch back to an earlier version, or delete versions you don't need. Deleting the version in use stops translation until you use another one or train again.",
    ta: "ஒவ்வொரு பயிற்சியும் ஒரு பதிப்பாகச் சேமிக்கப்படுகிறது. 'பயன்பாட்டில்' எனக் குறிக்கப்பட்டதை மொழிபெயர்ப்பாளர் பயன்படுத்துகிறது: முந்தைய பதிப்புக்கு மாறலாம், தேவையில்லாதவற்றை நீக்கலாம். பயன்பாட்டில் உள்ளதை நீக்கினால், வேறொன்றைத் தேர்ந்தெடுக்கும் வரை அல்லது மீண்டும் பயிற்சி அளிக்கும் வரை மொழிபெயர்ப்பு நிற்கும்.",
  },
  trainedAt: { en: "Trained", ta: "பயிற்சி நாள்" },
  modelInUse: { en: "In use", ta: "பயன்பாட்டில்" },
  useModel: { en: "Use this model", ta: "இதைப் பயன்படுத்து" },
  modelMissing: { en: "File missing", ta: "கோப்பு இல்லை" },
  noModels: {
    en: "No trained models. Train one on the Recordings tab.",
    ta: "பயிற்சி பெற்ற மாதிரிகள் இல்லை. 'பதிவுகள்' தாவலில் பயிற்சி அளியுங்கள்.",
  },
  confirmDeleteModel: { en: "Delete this trained model? This can't be undone.", ta: "இந்தப் பயிற்சி பெற்ற மாதிரியை நீக்கவா? இதைத் திரும்பப் பெற முடியாது." },
  confirmDeleteActiveModel: {
    en: "The translator is using this model. Delete it anyway? Translation stops until you use another model or train again.",
    ta: "மொழிபெயர்ப்பாளர் இந்த மாதிரியைப் பயன்படுத்துகிறது. இருந்தாலும் நீக்கவா? வேறொன்றைப் பயன்படுத்தும் வரை அல்லது மீண்டும் பயிற்சி அளிக்கும் வரை மொழிபெயர்ப்பு நிற்கும்.",
  },
  modelDeleted: { en: "Model deleted.", ta: "மாதிரி நீக்கப்பட்டது." },
  activeModelDeleted: {
    en: "Model deleted. The translator has no model now - use another version or train again.",
    ta: "மாதிரி நீக்கப்பட்டது. மொழிபெயர்ப்பாளருக்கு இப்போது மாதிரி இல்லை - வேறொரு பதிப்பைப் பயன்படுத்துங்கள் அல்லது மீண்டும் பயிற்சி அளியுங்கள்.",
  },
  modelActivated: { en: "The translator now uses this model.", ta: "மொழிபெயர்ப்பாளர் இப்போது இந்த மாதிரியைப் பயன்படுத்துகிறது." },
  errModelMissing: {
    en: "This model's files are missing, so it can't be used.",
    ta: "இந்த மாதிரியின் கோப்புகள் இல்லை, அதனால் பயன்படுத்த முடியாது.",
  },
  trainModelTitle: { en: "Train the model", ta: "மாதிரிக்குப் பயிற்சி" },
  trainApprovedHint: {
    en: "Training uses only approved recordings of approved words; each word needs at least {min}.",
    ta: "ஏற்கப்பட்ட சொற்களின் ஏற்கப்பட்ட பதிவுகள் மட்டுமே பயிற்சிக்குப் பயன்படும்; ஒவ்வொரு சொல்லுக்கும் குறைந்தது {min} தேவை.",
  },
  wordsReady: { en: "Words ready to train", ta: "பயிற்சிக்குத் தயாரான சொற்கள்" },
  approvedRecordings: { en: "Approved recordings", ta: "ஏற்கப்பட்ட பதிவுகள்" },
  waitingReview: { en: "Waiting for review", ta: "சரிபார்ப்புக்குக் காத்திருப்பவை" },
  newWordsWaiting: { en: "New words to approve", ta: "ஒப்புதலுக்கான புதிய சொற்கள்" },
  wordsToReview: { en: "Words", ta: "சொற்கள்" },
  needsReview: { en: "Needs review", ta: "சரிபார்க்க வேண்டியவை" },
  allWithRecordings: { en: "All with recordings", ta: "பதிவுகள் உள்ள அனைத்தும்" },
  queueEmpty: { en: "Nothing is waiting for review. 🎉", ta: "சரிபார்க்க எதுவும் காத்திருக்கவில்லை. 🎉" },
  noRecordingsYet: { en: "No recordings yet.", ta: "இன்னும் பதிவுகள் இல்லை." },
  pickWordToReview: { en: "Pick a word to see its recordings.", ta: "பதிவுகளைப் பார்க்க ஒரு சொல்லைத் தேர்ந்தெடுக்கவும்." },
  newWord: { en: "New word", ta: "புதிய சொல்" },
  wordAwaitsApproval: { en: "New word waiting for approval", ta: "ஒப்புதலுக்குக் காத்திருக்கும் புதிய சொல்" },
  wordWasRejected: { en: "This word was rejected", ta: "இந்தச் சொல் நிராகரிக்கப்பட்டது" },
  proposedBy: { en: "Proposed by", ta: "பரிந்துரைத்தவர்" },
  noteForTrainer: { en: "Note for the trainer (optional)", ta: "பயிற்சியாளருக்கான குறிப்பு (விருப்பத்தேர்வு)" },
  approveWord: { en: "Approve word", ta: "சொல்லை ஏற்கவும்" },
  rejectWord: { en: "Reject word", ta: "சொல்லை நிராகரி" },
  approveWordFirst: {
    en: "Approve the word itself before approving its recordings.",
    ta: "பதிவுகளை ஏற்பதற்கு முன் சொல்லை ஏற்கவும்.",
  },
  editWord: { en: "Edit word", ta: "சொல்லைத் திருத்து" },
  save: { en: "Save", ta: "சேமி" },
  wordUpdated: { en: "Word updated", ta: "சொல் புதுப்பிக்கப்பட்டது" },
  filter_pending: { en: "Waiting", ta: "காத்திருப்பு" },
  filter_approved: { en: "Approved", ta: "ஏற்கப்பட்டவை" },
  filter_rejected: { en: "Rejected", ta: "நிராகரிக்கப்பட்டவை" },
  filter_all: { en: "All", ta: "அனைத்தும்" },
  markAllShown: { en: "Mark all {n} shown:", ta: "காட்டப்படும் {n} பதிவுகளையும்:" },
  deleteAllRecordings: { en: "Delete all recordings", ta: "அனைத்துப் பதிவுகளையும் நீக்கு" },
  confirmDeleteRecordings: {
    en: "Delete every recording of this word from all trainers ({n} submitted, plus any unsubmitted drafts)? The word stays. This can't be undone.",
    ta: "இந்தச் சொல்லின் அனைத்துப் பயிற்சியாளர்களின் பதிவுகளையும் நீக்கவா ({n} சமர்ப்பிக்கப்பட்டவை, சமர்ப்பிக்கப்படாத வரைவுகளும்)? சொல் அப்படியே இருக்கும். இதைத் திரும்பப் பெற முடியாது.",
  },
  recordingsDeleted: {
    en: "Deleted {n} recordings and emailed the trainers. Train the model again so it forgets them.",
    ta: "{n} பதிவுகள் நீக்கப்பட்டு பயிற்சியாளர்களுக்கு மின்னஞ்சல் அனுப்பப்பட்டது. மாதிரி அவற்றை மறக்க மீண்டும் பயிற்சி அளியுங்கள்.",
  },
  approveAll: { en: "Approve all", ta: "அனைத்தையும் ஏற்கவும்" },
  rejectAll: { en: "Reject all", ta: "அனைத்தையும் நிராகரி" },
  all: { en: "All", ta: "அனைத்தும்" },
  approve: { en: "Approve", ta: "ஏற்கவும்" },
  reject: { en: "Reject", ta: "நிராகரி" },
  importedRecordings: { en: "Imported / earlier recordings", ta: "இறக்குமதி / முந்தைய பதிவுகள்" },
  handsVisible: { en: "Frames with hands visible", ta: "கைகள் தெரியும் சட்டங்கள்" },
  noRecordingsHere: { en: "No recordings in this list.", ta: "இந்தப் பட்டியலில் பதிவுகள் இல்லை." },
  decisionsSummary: { en: "{a} to approve · {r} to reject", ta: "ஏற்க {a} · நிராகரிக்க {r}" },
  rejectNotePlaceholder: {
    en: "Why rejected? (emailed to the trainer)",
    ta: "ஏன் நிராகரிப்பு? (பயிற்சியாளருக்கு மின்னஞ்சல் செய்யப்படும்)",
  },
  clearMarks: { en: "Clear", ta: "அழி" },
  saveReview: { en: "Save review", ta: "சரிபார்ப்பைச் சேமி" },
  reviewSaved: {
    en: "Saved {n} decisions. The trainers were notified by email.",
    ta: "{n} முடிவுகள் சேமிக்கப்பட்டன. பயிற்சியாளர்களுக்கு மின்னஞ்சல் அனுப்பப்பட்டது.",
  },
  play: { en: "Play", ta: "இயக்கு" },
  pause: { en: "Pause", ta: "இடைநிறுத்து" },
  recordingPreview: { en: "Recording replay", ta: "பதிவு மறுஇயக்கம்" },
  name: { en: "Name", ta: "பெயர்" },
  details: { en: "Details", ta: "விவரங்கள்" },
  recordings: { en: "Recordings", ta: "பதிவுகள்" },
  active: { en: "Active", ta: "செயலில்" },
  disabled: { en: "Disabled", ta: "முடக்கப்பட்டது" },
  disable: { en: "Disable", ta: "முடக்கு" },
  enable: { en: "Enable", ta: "இயக்கு" },
  notVerified: { en: "Email not verified", ta: "மின்னஞ்சல் சரிபார்க்கப்படவில்லை" },
  confirmDisable: {
    en: "Disable this account? They are logged out and can't log in until you enable it again.",
    ta: "இந்தக் கணக்கை முடக்கவா? அவர் வெளியேற்றப்படுவார்; மீண்டும் இயக்கும் வரை உள்நுழைய முடியாது.",
  },

  // Errors from the backend, by code (components/ErrorNote.jsx)
  errInvalidCredentials: { en: "Incorrect email or password.", ta: "மின்னஞ்சல் அல்லது கடவுச்சொல் தவறு." },
  errEmailNotVerified: {
    en: "This email isn't verified yet. Register again with it to get a new code.",
    ta: "இந்த மின்னஞ்சல் இன்னும் சரிபார்க்கப்படவில்லை. புதிய குறியீட்டைப் பெற மீண்டும் பதிவு செய்யுங்கள்.",
  },
  errAccountDisabled: {
    en: "This account has been disabled - please contact the admin.",
    ta: "இந்தக் கணக்கு முடக்கப்பட்டுள்ளது - நிர்வாகியைத் தொடர்பு கொள்ளவும்.",
  },
  errEmailTaken: {
    en: "An account with this email already exists - log in instead.",
    ta: "இந்த மின்னஞ்சலுடன் ஏற்கனவே கணக்கு உள்ளது - உள்நுழையவும்.",
  },
  errNoAccount: {
    en: "No account found for this email - please register first.",
    ta: "இந்த மின்னஞ்சலுக்குக் கணக்கு இல்லை - முதலில் பதிவு செய்யவும்.",
  },
  errAlreadyVerified: {
    en: "This email is already verified - log in instead.",
    ta: "இந்த மின்னஞ்சல் ஏற்கனவே சரிபார்க்கப்பட்டது - உள்நுழையவும்.",
  },
  errOtpInvalid: { en: "Wrong code - {remaining} attempt(s) left.", ta: "தவறான குறியீடு - இன்னும் {remaining} முயற்சி(கள்) உள்ளன." },
  errOtpExpired: {
    en: "This code has expired or was already used - ask for a new one.",
    ta: "இந்தக் குறியீடு காலாவதியானது அல்லது ஏற்கனவே பயன்படுத்தப்பட்டது - புதியதைக் கேளுங்கள்.",
  },
  errOtpTooMany: { en: "Too many wrong attempts - ask for a new code.", ta: "அதிகமான தவறான முயற்சிகள் - புதிய குறியீட்டைக் கேளுங்கள்." },
  errOtpCooldown: {
    en: "Please wait {retry_after} seconds before asking for another code.",
    ta: "மற்றொரு குறியீட்டைக் கேட்க {retry_after} வினாடிகள் காத்திருக்கவும்.",
  },
  errEmailFailed: {
    en: "The email couldn't be sent - please try again later.",
    ta: "மின்னஞ்சலை அனுப்ப முடியவில்லை - பின்னர் மீண்டும் முயற்சிக்கவும்.",
  },
  errLoginRequired: { en: "Please log in as a trainer or admin.", ta: "பயிற்சியாளர் அல்லது நிர்வாகியாக உள்நுழையவும்." },
  errSessionExpired: {
    en: "Your login has expired - please log in again.",
    ta: "உங்கள் உள்நுழைவு காலாவதியானது - மீண்டும் உள்நுழையவும்.",
  },
  errAdminOnly: { en: "Only an admin can do this.", ta: "நிர்வாகி மட்டுமே இதைச் செய்ய முடியும்." },
  errWrongPassword: { en: "The current password is incorrect.", ta: "தற்போதைய கடவுச்சொல் தவறு." },
  errWordExists: { en: "This word is already in the vocabulary.", ta: "இந்தச் சொல் ஏற்கனவே சொல்லகராதியில் உள்ளது." },
  errWordPending: {
    en: "This word was already proposed and is waiting for review.",
    ta: "இந்தச் சொல் ஏற்கனவே பரிந்துரைக்கப்பட்டு சரிபார்ப்புக்குக் காத்திருக்கிறது.",
  },
  errWordNotApproved: {
    en: "Approve the word itself before approving its recordings.",
    ta: "பதிவுகளை ஏற்பதற்கு முன் சொல்லை ஏற்கவும்.",
  },
  errSignAlreadyUsed: {
    en: "Not saved: this sign already belongs to another word ({pct}% match). Show this word's own sign. It matched:",
    ta: "சேமிக்கப்படவில்லை: இந்தச் சைகை ஏற்கனவே வேறொரு சொல்லுக்குரியது ({pct}% பொருத்தம்). இந்தச் சொல்லுக்குரிய சைகையைச் செய்யுங்கள். பொருந்திய சொல்:",
  },
  errIdleLooksLikeSign: {
    en: "Not saved: this looks like a sign ({pct}% match), not resting hands. Idle recordings must not show a sign. It matched:",
    ta: "சேமிக்கப்படவில்லை: இது ஓய்வான கைகளாக அல்ல, ஒரு சைகையாகத் தெரிகிறது ({pct}% பொருத்தம்). ஓய்வுப் பதிவுகளில் சைகை இருக்கக்கூடாது. பொருந்திய சொல்:",
  },
  switchToWord: { en: "Record it for", ta: "இதற்காகப் பதிவு செய்" },
  errNoRecordings: { en: "This word has no recordings.", ta: "இந்தச் சொல்லுக்குப் பதிவுகள் இல்லை." },
  errNothingToSubmit: { en: "There are no draft recordings to submit.", ta: "சமர்ப்பிக்க வரைவுப் பதிவுகள் இல்லை." },
  errAlreadyReviewed: { en: "Reviewed recordings can't be deleted.", ta: "சரிபார்க்கப்பட்ட பதிவுகளை நீக்க முடியாது." },
  errNotAllowed: {
    en: "You can only delete words you proposed that haven't been approved.",
    ta: "நீங்கள் பரிந்துரைத்த, இன்னும் ஏற்கப்படாத சொற்களை மட்டுமே நீக்க முடியும்.",
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

/** A date from the API (ISO string) for display; `withTime` adds the time of day. */
export function formatDate(iso, lang, withTime = false) {
  if (!iso) return "";
  const options = { day: "numeric", month: "short", year: "numeric" };
  if (withTime) Object.assign(options, { hour: "2-digit", minute: "2-digit" });
  return new Date(iso).toLocaleString(lang === "ta" ? "ta-IN" : "en-IN", options);
}
