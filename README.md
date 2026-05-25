STORAVEL DJANGO BACKEND (MVP CLEAN ARCHITECTURE)

═══════════════════════════════════════════
You are a senior Django + DRF engineer. Build a production-ready REST API for a language learning platform called "Storavel".

This system is a content-first language learning platform (NO AI generation, NO background workers). All learning materials are manually created and managed via admin panel or API.

The goal is scalability, simplicity, and clean architecture.

🧱 TECH STACK
Python 3.12+
Django 5.x
Django REST Framework
PostgreSQL
Simple JWT (authentication)
django-filter (search & filtering)
drf-spectacular (OpenAPI documentation)
django-cors-headers
Pillow (image processing)
django-cloudinary-storage (media handling)
Cloudinary (image CDN)
❌ EXCLUDED SYSTEMS

DO NOT USE:

Celery
Redis
OpenAI / AI APIs
AWS S3
Background jobs
Message queues
Microservices

All operations must be synchronous and simple.

📁 PROJECT STRUCTURE

storavel_backend/
├── config/
│ ├── settings/
│ │ ├── base.py
│ │ ├── development.py
│ │ └── production.py
│ ├── urls.py
│ ├── wsgi.py
│ └── asgi.py
├── apps/
│ ├── accounts/
│ ├── languages/
│ ├── stories/
│ ├── vocabulary/
│ ├── quizzes/
│ ├── notebooks/
│ └── progress/
├── core/
│ ├── permissions.py
│ ├── pagination.py
│ ├── mixins.py
│ └── utils.py
└── manage.py

🔐 ACCOUNTS APP
User Model

Custom user with UUID primary key.

Fields:

id (UUID)
email (unique, login field)
username
display_name
avatar (Cloudinary image)
bio
native_language (FK → Language)
is_premium (bool)
timezone
created_at / updated_at

Authentication:

Simple JWT
Access token (15 min)
Refresh token (30 days)
UserSettings
dark_mode
ui_language
notifications_enabled
streak_reminder_time
font_size (sm/md/lg)
show_romanization
auto_play_audio
🌍 LANGUAGES APP
Language Model
code (e.g. en, sv, de, ja)
name
native_name
flag_emoji
script (latin, arabic, cjk, cyrillic)
rtl (bool)
has_romanization (bool)
is_active
order
UserTargetLanguage
user
language
is_primary
added_at

Unique constraint: user + language

📖 STORIES APP (CORE SYSTEM)
Story Model

Fields:

id (UUID)
language (FK)
title
slug (unique)
level_min (A1–C2)
level_max (A1–C2)
story_type:
narrative
dialog
news
business
academic
cover_image (Cloudinary)
estimated_read_minutes
is_premium
is_published
order
tags (ManyToMany → StoryTag)
StoryTag
name
slug
StoryVersion

Each story has multiple manually created versions:

Types:

original
present
past
future
native
dialog
idioms
emotional
vocabulary
qa

Fields:

id (UUID)
story (FK)
version_type
content (full text)
word_count
created_at
updated_at

Unique constraint:
story + version_type

UserStoryProgress

Tracks user progress per story:

user
story
last_version_read
versions_read (JSON list)
completed (bool)
read_count
last_read_at
quiz_best_score
time_spent_seconds
UserNote
user
story
content
created_at
updated_at
📚 VOCABULARY APP
Word (Master Vocabulary)
id (UUID)
language
word
part_of_speech:
noun, verb, adjective, adverb, phrase, idiom, etc.
definition
romanization
audio_url (optional)
difficulty_level (A1–C2)

Unique:
language + word

WordTranslation
word
target_language
translation
WordSynonym
word
synonym
StoryWord

Links vocabulary to stories:

story
word
example_sentence
order
📒 NOTEBOOK APP (MY WORDS)
UserWord

User saved vocabulary:

Fields:

id (UUID)
user
language
word
part_of_speech
definition
example_sentence
translation
synonyms (JSON)
romanization
audio_url

Source references:

source_story (nullable FK)
source_word (nullable FK)
Learning metadata (SM-2 SYSTEM)
status:
new
learning
reviewing
mastered
times_reviewed
last_reviewed_at
next_review_at
ease_factor (default 2.5)
UserWordCollection
user
name
description
color (hex)
icon
words (ManyToMany)
🧠 SM-2 SPACED REPETITION (IMPORTANT)

Implemented in:

Endpoint:

POST /notebook/words/{id}/review/

Logic:

Input:

quality (0–5)

Algorithm:

adjust ease_factor
calculate interval
schedule next_review_at
update status:
new → learning → reviewing → mastered

NO background jobs required.

🧪 QUIZZES APP
Quiz
id (UUID)
story
version_type
title
is_premium
QuizQuestion

Types:

true_false
fill_blank
multiple_choice
translation

Fields:

question_text
hint_text
correct_answer
options (JSON)
explanation
UserQuizAttempt
user
quiz
score (0–100)
correct_answers
total_questions
answers (JSON)
time_taken_seconds
📊 PROGRESS APP
UserProgress
user
language
total_stories_read
total_words_learned
total_quiz_attempts
total_xp
current_streak_days
longest_streak_days
last_active_date
DailyActivity
user
date
stories_read
words_reviewed
quizzes_taken
xp_earned
minutes_spent
Achievement
code
title
description
icon
xp_reward
condition_type
condition_value
UserAchievement
user
achievement
earned_at
🌐 API ENDPOINTS
AUTH
POST /auth/register/
POST /auth/login/
POST /auth/token/refresh/
GET /auth/me/
PATCH /auth/me/
LANGUAGES
GET /languages/
GET /languages/{code}/
GET /languages/me/
POST /languages/me/
DELETE /languages/me/{code}/
STORIES
GET /stories/
GET /stories/{slug}/
GET /stories/{slug}/versions/
GET /stories/{slug}/versions/{type}/
GET /stories/{slug}/words/
GET /stories/{slug}/progress/
POST /stories/{slug}/progress/
GET /stories/{slug}/note/
PUT /stories/{slug}/note/
VOCABULARY
GET /vocabulary/words/
GET /vocabulary/words/{id}/
NOTEBOOK
GET /notebook/words/
POST /notebook/words/
GET /notebook/words/{id}/
PATCH /notebook/words/{id}/
DELETE /notebook/words/{id}/
POST /notebook/words/{id}/favorite/
POST /notebook/words/{id}/review/
GET /notebook/words/due-review/
GET /notebook/export/
COLLECTIONS
GET /notebook/collections/
POST /notebook/collections/
PATCH /notebook/collections/{id}/
DELETE /notebook/collections/{id}/
POST /notebook/collections/{id}/words/add/
POST /notebook/collections/{id}/words/remove/
QUIZZES
GET /quizzes/stories/{slug}/
POST /quizzes/stories/{slug}/attempt/
GET /quizzes/history/
PROGRESS
GET /progress/
GET /progress/streak/
GET /progress/activity/
GET /progress/achievements/
🖼 MEDIA STORAGE

Use Cloudinary for:

user avatars
story cover images

No S3 usage.

🔐 THROTTLING
Anonymous: 60 req/hour
Authenticated: 1000 req/hour
Notebook review: 2000 req/hour
🧪 TESTING

Use pytest-django:

Cover:

models
API endpoints
SM-2 logic
permissions
serializers
🚀 DEPLOYMENT
Django → Render
PostgreSQL → Render DB
Frontend → Vercel
Media → Cloudinary
📌 DESIGN PRINCIPLES
Keep API RESTful
Avoid overengineering
No async systems
No external workers
Keep everything deterministic
Admin panel is primary content source