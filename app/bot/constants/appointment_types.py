import enum


class AppointmentType(str, enum.Enum):
    IN_PERSON = "in_person"


APPOINTMENT_TYPE_LABELS: dict[AppointmentType, str] = {
    AppointmentType.IN_PERSON: "🏥 ویزیت حضوری",
}


def get_appointment_type_label(value: str) -> str:
    try:
        return APPOINTMENT_TYPE_LABELS[AppointmentType(value)]
    except (ValueError, KeyError):
        return value
