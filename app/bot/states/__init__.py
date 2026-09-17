from app.bot.bale_compat import State, StatesGroup


class BookingStates(StatesGroup):
    select_specialty = State()
    select_doctor = State()
    select_appointment_type = State()
    select_date = State()
    select_time = State()
    enter_phone = State()
    enter_name = State()
    confirm = State()


class CancelAppointmentStates(StatesGroup):
    select_appointment = State()
    confirm = State()


class AdminSpecialtyStates(StatesGroup):
    enter_name = State()
    enter_description = State()
    edit_name = State()
    edit_description = State()


class AdminDoctorStates(StatesGroup):
    select_specialty = State()
    enter_name = State()
    enter_bio = State()
    edit_name = State()
    edit_bio = State()
    edit_specialty = State()


class AdminScheduleStates(StatesGroup):
    select_doctor = State()
    enter_date = State()
    enter_start_time = State()
    enter_end_time = State()
    enter_duration = State()
    edit_date = State()
    edit_start_time = State()
    edit_end_time = State()
    edit_duration = State()


class AdminAppointmentStates(StatesGroup):
    search_query = State()


class AdminAnnouncementStates(StatesGroup):
    enter_title = State()
    enter_content = State()
    edit_title = State()
    edit_content = State()


class AdminContentStates(StatesGroup):
    enter_address = State()
    enter_support = State()


class AdminBroadcastStates(StatesGroup):
    enter_message = State()
    confirm = State()


class AdminManageStates(StatesGroup):
    enter_bale_user_id = State()
    enter_display_name = State()
