# Main menu
MAIN_MENU = "🏥 منوی اصلی کلینیک\n\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:"

BTN_NEW_APPOINTMENT = "📅 رزرو نوبت جدید"
BTN_MY_APPOINTMENTS = "📋 نوبت‌های من"
BTN_ADDRESS = "📍 آدرس"
BTN_SUPPORT = "💬 پشتیبانی"
BTN_BACK = "🔙 بازگشت"
BTN_CANCEL = "❌ انصراف"
BTN_CONFIRM = "✅ تأیید"
BTN_MAIN_MENU = "🏠 منوی اصلی"

# Address & Support
ADDRESS_NOT_SET = "📍 آدرس هنوز ثبت نشده است.\n\nادمین می‌تواند از پنل مدیریت آن را تنظیم کند."
SUPPORT_NOT_SET = "💬 اطلاعات پشتیبانی هنوز ثبت نشده است.\n\nادمین می‌تواند از پنل مدیریت آن را تنظیم کند."

ADDRESS_TEXT = (
    "📍 آدرس کلینیک:\n\n"
    "تهران، خیابان ولیعصر، پلاک ۱۲۳\n"
    "طبقه دوم، واحد ۵\n\n"
    "🕐 ساعات کاری: شنبه تا پنجشنبه ۸ تا ۲۰"
)

SUPPORT_TEXT = (
    "💬 پشتیبانی\n\n"
    "برای ارتباط با پشتیبانی با شماره زیر تماس بگیرید:\n"
    "📞 ۰۲۱-۱۲۳۴۵۶۷۸\n\n"
    "یا پیام خود را در همین ربات ارسال کنید."
)

# Booking flow
SELECT_SPECIALTY = "🏷 لطفاً تخصص مورد نظر خود را انتخاب کنید:"
SELECT_DOCTOR = "👨‍⚕️ لطفاً پزشک مورد نظر خود را انتخاب کنید:"
SELECT_DATE = "📅 لطفاً تاریخ نوبت را انتخاب کنید:"
SELECT_TIME = "🕐 لطفاً ساعت نوبت را انتخاب کنید:"
ENTER_PHONE = (
    "📱 لطفاً شماره موبایل خود را ارسال کنید.\n\n"
    "می‌توانید از دکمه «اشتراک‌گذاری شماره تماس» استفاده کنید "
    "یا شماره را به صورت دستی تایپ کنید (مثال: ۰۹۱۲۳۴۵۶۷۸۹)."
)
ENTER_NAME = "👤 لطفاً نام و نام خانوادگی بیمار را وارد کنید:"
BTN_SHARE_PHONE = "📱 اشتراک‌گذاری شماره تماس"
CONFIRM_BOOKING = (
    "📋 خلاصه نوبت:\n\n"
    "🔖 کد پیگیری: {tracking_preview}\n"
    "تخصص: {specialty}\n"
    "پزشک: {doctor}\n"
    "تاریخ: {date}\n"
    "ساعت: {time}\n"
    "نام بیمار: {name}\n"
    "موبایل: {phone}\n\n"
    "آیا از ثبت این نوبت اطمینان دارید؟"
)

BOOKING_SUCCESS = (
    "✅ نوبت شما با موفقیت ثبت شد!\n\n"
    "🔖 کد پیگیری: {tracking_code}\n"
    "تخصص: {specialty}\n"
    "پزشک: {doctor}\n"
    "تاریخ: {date}\n"
    "ساعت: {time}\n\n"
    "لطفاً کد پیگیری را یادداشت کنید.\n"
    "۱۵ دقیقه قبل از وقت نوبت در کلینیک حضور داشته باشید."
)

BOOKING_IN_PROGRESS = (
    "⚠️ شما یک رزرو ناتمام دارید.\n\n"
    "آیا می‌خواهید از همانجا ادامه دهید یا رزرو جدید شروع کنید؟"
)
BTN_RESUME_BOOKING = "▶️ ادامه رزرو"
BTN_NEW_BOOKING = "🔄 رزرو جدید"
STATE_RECOVERED = "✅ رزرو شما بازیابی شد. لطفاً ادامه دهید."
LOCK_EXPIRED = "⏱ زمان رزرو شما منقضی شده است. لطفاً دوباره ساعت را انتخاب کنید."
BTN_CANCEL_APPOINTMENT = "🗑 لغو این نوبت"

NO_SPECIALTIES = "در حال حاضر تخصصی برای رزرو نوبت تعریف نشده است."
NO_DOCTORS = "در حال حاضر پزشکی برای این تخصص موجود نیست."
NO_AVAILABLE_APPOINTMENTS = "متأسفانه در حال حاضر نوبت خالی برای این پزشک وجود ندارد."
NO_AVAILABLE_DATES = "متأسفانه تاریخ خالی برای رزرو وجود ندارد."
NO_AVAILABLE_SLOTS = "متأسفانه ساعت خالی برای این تاریخ وجود ندارد."
SLOT_TAKEN = "این ساعت قبلاً رزرو شده یا در حال رزرو توسط کاربر دیگری است. لطفاً ساعت دیگری انتخاب کنید."
INVALID_NAME = "نام وارد شده نامعتبر است. لطفاً حداقل ۳ کاراکتر وارد کنید."
INVALID_PHONE = "شماره موبایل نامعتبر است. لطفاً شماره ۱۱ رقمی با پیش‌شماره ۰۹ وارد کنید."
BOOKING_CANCELLED = "رزرو نوبت لغو شد."

# My appointments
MY_APPOINTMENTS_EMPTY = "شما هیچ نوبت فعالی ندارید."
MY_APPOINTMENTS_HEADER = "📋 نوبت‌های فعال شما:"
APPOINTMENT_ITEM = (
    "🔖 کد پیگیری: {tracking_code}\n"
    "پزشک: {doctor} ({specialty})\n"
    "تاریخ: {date} — ساعت: {time}\n"
    "وضعیت: {status}"
)
SELECT_APPOINTMENT_TO_CANCEL = "برای مشاهده جزئیات یا لغو نوبت، یکی از موارد زیر را انتخاب کنید:"
APPOINTMENT_DETAILS = (
    "📋 جزئیات نوبت:\n\n"
    "🔖 کد پیگیری: {tracking_code}\n"
    "پزشک: {doctor}\n"
    "تخصص: {specialty}\n"
    "تاریخ: {date}\n"
    "ساعت: {time}\n"
    "نام بیمار: {name}\n"
    "موبایل: {phone}\n"
    "وضعیت: {status}"
)
CONFIRM_CANCEL = "آیا از لغو این نوبت اطمینان دارید؟\n\n{details}"
CANCEL_SUCCESS = "✅ نوبت شما با موفقیت لغو شد."
CANCEL_FAILED = "امکان لغو این نوبت وجود ندارد."

STATUS_CONFIRMED = "✅ تأیید شده"
STATUS_CANCELLED = "❌ لغو شده"
STATUS_COMPLETED = "🏁 انجام شده"
STATUS_NO_SHOW = "⚠️ عدم حضور"

# Reminders
REMINDER_24H_MESSAGE = (
    "🔔 یادآوری نوبت — ۲۴ ساعت مانده\n\n"
    "نوبت شما فردا است:\n\n"
    "🔖 کد پیگیری: {tracking_code}\n"
    "پزشک: {doctor}\n"
    "تاریخ: {date}\n"
    "ساعت: {time}\n\n"
    "لطفاً به موقع در کلینیک حضور داشته باشید."
)

REMINDER_2H_MESSAGE = (
    "🔔 یادآوری نوبت — ۲ ساعت مانده\n\n"
    "نوبت شما به زودی است:\n\n"
    "🔖 کد پیگیری: {tracking_code}\n"
    "پزشک: {doctor}\n"
    "تاریخ: {date}\n"
    "ساعت: {time}\n\n"
    "لطفاً ۱۵ دقیقه زودتر حضور داشته باشید."
)

# Notifications
NOTIFY_ADMIN_NEW_APPOINTMENT = (
    "🆕 رزرو نوبت جدید\n\n"
    "🔖 کد: {tracking_code}\n"
    "بیمار: {patient_name}\n"
    "موبایل: {phone}\n"
    "پزشک: {doctor}\n"
    "تاریخ: {date} — ساعت: {time}"
)

NOTIFY_ADMIN_CANCELLED = (
    "❌ لغو نوبت\n\n"
    "🔖 کد: {tracking_code}\n"
    "بیمار: {patient_name}\n"
    "پزشک: {doctor}\n"
    "تاریخ: {date} — ساعت: {time}"
)

NOTIFY_USER_CANCELLED = (
    "❌ نوبت شما لغو شد.\n\n"
    "🔖 کد پیگیری: {tracking_code}\n"
    "پزشک: {doctor}\n"
    "تاریخ: {date}\n"
    "ساعت: {time}"
)

NOTIFY_USER_BOOKING_CONFIRMED = (
    "✅ تأیید رزرو نوبت\n\n"
    "🔖 کد پیگیری: {tracking_code}\n"
    "پزشک: {doctor}\n"
    "تاریخ: {date}\n"
    "ساعت: {time}\n\n"
    "پیامک/یادآوری ۲۴ و ۲ ساعت قبل از نوبت ارسال خواهد شد."
)

NOTIFY_ADMIN_ERROR = (
    "⚠️ خطای سیستم\n\n"
    "بخش: {context}\n"
    "خطا: {error}"
)

NOTIFY_ADMIN_JOB_SUCCESS = "✅ کار پس‌زمینه «{job}» با موفقیت اجرا شد."
NOTIFY_STATS_GENERATED = (
    "📊 آمار روزانه ذخیره شد — {date}\n\n"
    "کاربران جدید: {new_users}\n"
    "رزروهای جدید: {new_appointments}\n"
    "رزروهای فعال: {confirmed}"
)

# Legacy (kept for compatibility)
REMINDER_MESSAGE = REMINDER_24H_MESSAGE

# Admin
ADMIN_MENU = "🛠 پنل مدیریت\n\nنقش شما: {role}\n\nلطفاً یکی از گزینه‌ها را انتخاب کنید:"
BTN_ADMIN_SPECIALTIES = "🏷 مدیریت تخصص‌ها"
BTN_ADMIN_DOCTORS = "👨‍⚕️ مدیریت پزشکان"
BTN_ADMIN_SCHEDULES = "📆 مدیریت زمان‌بندی"
BTN_ADMIN_APPOINTMENTS = "📋 مدیریت رزروها"
BTN_ADMIN_ANNOUNCEMENTS = "📣 مدیریت اعلامیه‌ها"
BTN_ADMIN_ADDRESS = "📍 مدیریت آدرس"
BTN_ADMIN_SUPPORT = "💬 مدیریت پشتیبانی"
BTN_ADMIN_ADMINS = "👥 مدیریت ادمین‌ها"
BTN_ADMIN_SETTINGS = "⚙️ تنظیمات"
BTN_ADMIN_STATS = "📊 آمار سیستم"
BTN_ADMIN_BROADCAST = "📢 ارسال پیام همگانی"
BTN_ADMIN_EXIT = "🔙 خروج از پنل"
BTN_EDIT = "✏️ ویرایش"
BTN_DELETE = "🗑 حذف"
BTN_SEARCH_APPOINTMENT = "🔍 جستجوی رزرو"
BTN_RECENT_APPOINTMENTS = "🕐 آخرین رزروها"
BTN_ADD_ANNOUNCEMENT = "➕ افزودن اعلامیه"
BTN_ADMIN_CANCEL_APPT = "❌ لغو نوبت"
BTN_MARK_COMPLETED = "✅ انجام شد"
BTN_MARK_NO_SHOW = "⚠️ عدم حضور"
BTN_PROMOTE_SUPER = "⭐ ارتقا به سوپرادمین"
BTN_DEMOTE_ADMIN = "👤 تنزل به ادمین"
BTN_VIEW_SETTINGS = "👁 مشاهده تنظیمات"
PERMISSION_DENIED = "⛔ شما دسترسی لازم برای این عملیات را ندارید."

NOT_ADMIN = "شما دسترسی مدیریت ندارید."

# Specialty admin
SPECIALTY_LIST_HEADER = "🏷 لیست تخصص‌ها:"
BTN_ADD_SPECIALTY = "➕ افزودن تخصص"
ENTER_SPECIALTY_NAME = "نام تخصص را وارد کنید:"
ENTER_SPECIALTY_DESC = "توضیحات تخصص را وارد کنید (یا /skip برای رد کردن):"
SPECIALTY_CREATED = "✅ تخصص «{name}» با موفقیت ایجاد شد."
SPECIALTY_UPDATED = "✅ تخصص با موفقیت به‌روزرسانی شد."
SELECT_SPECIALTY_TO_EDIT = "تخصص مورد نظر را برای ویرایش انتخاب کنید:"
SPECIALTY_DELETED = "✅ تخصص حذف شد."
SPECIALTY_DEACTIVATED = "✅ تخصص غیرفعال شد (به‌دلیل وجود پزشک مرتبط)."
ENTER_SPECIALTY_EDIT_NAME = "نام جدید تخصص را وارد کنید:"
ENTER_SPECIALTY_EDIT_DESC = "توضیحات جدید را وارد کنید (یا /skip):"
CONFIRM_DELETE = "⚠️ آیا از حذف «{name}» اطمینان دارید؟"
BTN_TOGGLE_ACTIVE = "🔄 تغییر وضعیت فعال/غیرفعال"

# Doctor admin
DOCTOR_LIST_HEADER = "👨‍⚕️ لیست پزشکان:"
BTN_ADD_DOCTOR = "➕ افزودن پزشک"
SELECT_SPECIALTY_FOR_DOCTOR = "تخصص پزشک را انتخاب کنید:"
ENTER_DOCTOR_NAME = "نام پزشک را وارد کنید:"
ENTER_DOCTOR_BIO = "بیوگرافی پزشک را وارد کنید (یا /skip برای رد کردن):"
DOCTOR_CREATED = "✅ پزشک «{name}» با موفقیت ایجاد شد."
DOCTOR_UPDATED = "✅ اطلاعات پزشک به‌روزرسانی شد."
DOCTOR_DELETED = "✅ پزشک غیرفعال شد."
ENTER_DOCTOR_EDIT_NAME = "نام جدید پزشک را وارد کنید:"
ENTER_DOCTOR_EDIT_BIO = "بیوگرافی جدید را وارد کنید (یا /skip):"
SELECT_DOCTOR_EDIT_SPECIALTY = "تخصص جدید پزشک را انتخاب کنید:"
SELECT_DOCTOR_TO_EDIT = "پزشک مورد نظر را برای ویرایش انتخاب کنید:"

# Schedule admin
SCHEDULE_LIST_HEADER = "📆 برنامه‌های {doctor}:"
BTN_ADD_SCHEDULE = "➕ افزودن برنامه"
SELECT_DOCTOR_FOR_SCHEDULE = "پزشک مورد نظر را انتخاب کنید:"
ENTER_SCHEDULE_DATE = "تاریخ برنامه را وارد کنید (مثال: 1404/06/20 یا 2025-09-11):"
ENTER_START_TIME = "ساعت شروع را وارد کنید (مثال: 16:00):"
ENTER_END_TIME = "ساعت پایان را وارد کنید (مثال: 20:00):"
ENTER_VISIT_DURATION = "مدت هر ویزیت را به دقیقه وارد کنید (مثال: 15):"
SCHEDULE_CREATED = (
    "✅ برنامه با موفقیت ایجاد شد.\n\n"
    "تاریخ: {date}\n"
    "ساعت: {start} تا {end}\n"
    "مدت ویزیت: {duration} دقیقه\n"
    "تعداد نوبت: {slot_count}"
)
INVALID_DATE = "تاریخ وارد شده نامعتبر است."
INVALID_TIME = "ساعت وارد شده نامعتبر است."
INVALID_DURATION = "مدت ویزیت باید عدد مثبت باشد."
INVALID_TIME_RANGE = "ساعت پایان باید بعد از ساعت شروع باشد."
SCHEDULE_EXISTS = "برنامه‌ای برای این پزشک در این تاریخ قبلاً ثبت شده است."
SCHEDULE_DELETED = "✅ برنامه حذف شد."
SCHEDULE_UPDATED = "✅ برنامه به‌روزرسانی شد."
SCHEDULE_DETAIL = (
    "📆 جزئیات برنامه:\n\n"
    "پزشک: {doctor}\n"
    "تاریخ: {date}\n"
    "ساعت: {start} تا {end}\n"
    "مدت ویزیت: {duration} دقیقه\n"
    "تعداد نوبت: {slot_count}"
)
SELECT_SCHEDULE_FIELD = "کدام بخش را ویرایش می‌کنید؟"
BTN_EDIT_DATE = "📅 تاریخ"
BTN_EDIT_START = "🕐 ساعت شروع"
BTN_EDIT_END = "🕑 ساعت پایان"
BTN_EDIT_DURATION = "⏱ مدت ویزیت"

# Appointments admin
APPOINTMENTS_ADMIN_MENU = "📋 مدیریت رزروها\n\nیک گزینه را انتخاب کنید:"
ENTER_SEARCH_QUERY = "کد پیگیری، نام بیمار یا شماره موبایل را وارد کنید:"
SEARCH_NO_RESULTS = "نتیجه‌ای یافت نشد."
APPOINTMENT_ADMIN_DETAIL = (
    "📋 جزئیات رزرو:\n\n"
    "🔖 کد: {tracking_code}\n"
    "بیمار: {name}\n"
    "موبایل: {phone}\n"
    "پزشک: {doctor}\n"
    "تخصص: {specialty}\n"
    "تاریخ: {date}\n"
    "ساعت: {time}\n"
    "وضعیت: {status}"
)
APPOINTMENT_STATUS_UPDATED = "✅ وضعیت رزرو به‌روزرسانی شد."

# Announcements
ANNOUNCEMENT_LIST_HEADER = "📣 لیست اعلامیه‌ها:"
ENTER_ANNOUNCEMENT_TITLE = "عنوان اعلامیه را وارد کنید:"
ENTER_ANNOUNCEMENT_CONTENT = "متن اعلامیه را وارد کنید:"
ANNOUNCEMENT_CREATED = "✅ اعلامیه «{title}» ایجاد شد."
ANNOUNCEMENT_UPDATED = "✅ اعلامیه به‌روزرسانی شد."
ANNOUNCEMENT_DELETED = "✅ اعلامیه حذف شد."
ANNOUNCEMENT_DETAIL = "📣 {title}\n\n{content}\n\nوضعیت: {status}"

# Address & Support admin
ADDRESS_ADMIN_HEADER = "📍 مدیریت آدرس کلینیک\n\nمتن فعلی:\n\n{current}"
SUPPORT_ADMIN_HEADER = "💬 مدیریت پشتیبانی\n\nمتن فعلی:\n\n{current}"
ENTER_NEW_ADDRESS = "متن جدید آدرس را وارد کنید:"
ENTER_NEW_SUPPORT = "متن جدید پشتیبانی را وارد کنید:"
ADDRESS_UPDATED = "✅ آدرس کلینیک به‌روزرسانی شد."
SUPPORT_UPDATED = "✅ اطلاعات پشتیبانی به‌روزرسانی شد."
BTN_EDIT_ADDRESS = "✏️ ویرایش آدرس"
BTN_EDIT_SUPPORT = "✏️ ویرایش پشتیبانی"

# Settings
SETTINGS_HEADER = (
    "⚙️ تنظیمات سیستم\n\n"
    "منطقه زمانی: {timezone}\n"
    "مدت قفل اسلات: {slot_lock} ثانیه\n"
    "یادآوری ۲۴ ساعته: {reminder_24h} ساعت قبل\n"
    "یادآوری ۲ ساعته: {reminder_2h} ساعت قبل\n"
    "گزارش روزانه: {report_hour:02d}:{report_minute:02d}\n"
    "فاصله بررسی یادآوری: {reminder_interval} دقیقه\n\n"
    "تنظیمات بالا از فایل env خوانده می‌شوند."
)

# Stats
SYSTEM_STATS = (
    "📊 آمار سیستم\n\n"
    "👤 کاربران: {total_users}\n"
    "👥 ادمین‌ها: {total_admins}\n"
    "🏷 تخصص‌های فعال: {total_specialties}\n"
    "👨‍⚕️ پزشکان فعال: {total_doctors}\n"
    "📆 برنامه‌ها: {total_schedules}\n"
    "📋 کل رزروها: {total_appointments}\n"
    "✅ رزروهای فعال: {confirmed}\n"
    "❌ لغوشده: {cancelled}\n"
    "🏁 انجام‌شده: {completed}\n"
    "📣 اعلامیه‌های فعال: {announcements}\n"
    "📅 رزروهای امروز: {today}"
)

# Admin management
ADMIN_DETAIL = "👤 {role}\n\nشناسه: {bale_user_id}\nنام: {name}\nوضعیت: {status}"
ADMIN_PROMOTED = "✅ ادمین به سوپرادمین ارتقا یافت."
ADMIN_DEMOTED = "✅ سوپرادمین به ادمین عادی تنزل یافت."
ENTER_ADMIN_NAME = "نام نمایشی ادمین را وارد کنید (یا /skip):"
ROLE_SUPERADMIN = "سوپرادمین"
ROLE_ADMIN = "ادمین"
STATUS_ACTIVE = "فعال"
STATUS_INACTIVE = "غیرفعال"
ENTER_BROADCAST_MESSAGE = "متن پیام همگانی را وارد کنید:"
CONFIRM_BROADCAST = "آیا از ارسال این پیام به {count} کاربر اطمینان دارید؟\n\n{message}"
BROADCAST_STARTED = "📢 ارسال پیام همگانی آغاز شد..."
BROADCAST_DONE = "✅ پیام همگانی ارسال شد.\nموفق: {sent}\nناموفق: {failed}"

# Report
DAILY_REPORT = (
    "📊 گزارش روزانه — {date}\n\n"
    "👤 کاربران جدید: {new_users}\n"
    "📅 نوبت‌های جدید: {new_appointments}\n"
    "❌ نوبت‌های لغو شده: {cancelled}\n\n"
    "📋 نوبت‌های امروز ({count}):\n{appointments}"
)
NO_APPOINTMENTS_TODAY = "امروز نوبتی ثبت نشده است."
REPORT_APPOINTMENT_LINE = "• {time} — {doctor} — {patient}"

# Admin management
ADMIN_LIST_HEADER = "👥 لیست ادمین‌ها:"
BTN_ADD_ADMIN = "➕ افزودن ادمین"
ENTER_ADMIN_ID = "شناسه بله ادمین جدید را وارد کنید:"
ADMIN_ADDED = "✅ ادمین با موفقیت اضافه شد."
ADMIN_REMOVED = "✅ ادمین حذف شد."
CANNOT_REMOVE_SUPERADMIN = "امکان حذف سوپرادمین وجود ندارد."
ADMIN_EXISTS = "این کاربر قبلاً ادمین است."

# General
UNKNOWN_COMMAND = "دستور نامعتبر است. لطفاً از منو استفاده کنید."
OPERATION_CANCELLED = "عملیات لغو شد."
ERROR_GENERIC = "خطایی رخ داد. لطفاً دوباره تلاش کنید."
