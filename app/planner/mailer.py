def send_confirm_email(*, course: Course, appointment: Appointment, test_moment: TestMoment, request: HttpRequest):
    url = request.build_absolute_uri(
        reverse("cancel", kwargs={"course_name": course.short_name, "secret": appointment.cancel_secret}))

    message = f'Je hebt je ingeschreven voor het maken van een toetsje op {_date(appointment.date, "l j F")} ' \
              f'om {_time(appointment.start_time)}.\r\nHet maken van dit toetsje vindt plaats in {test_moment.location}.\r\n' \
              f'Wil je de afspraak anuleren, dat kan via deze link {url}'

    if not settings.EMAIL_HOST:
        print(message)
        return

    send_mail(subject=f'Toetsje ingepland voor {course.name}',
              message=message,
              from_email=settings.EMAIL_FROM,
              recipient_list=[appointment.email])