import datetime
from datetime import timedelta

import pytest

from appkernel import ValidationException
from tests.utils import ExampleClass, Project, Task, Payment, PaymentMethod


def test_regexp_validation():
    test_model_correct_format = ExampleClass()
    test_model_correct_format.just_numbers = '123456'
    test_model_correct_format.finalise_and_validate()

    with pytest.raises(ValidationException):
        test_model_correct_format = ExampleClass()
        test_model_correct_format.just_numbers = 'pppppp1234566p3455pppp'
        test_model_correct_format.finalise_and_validate()

    with pytest.raises(ValidationException):
        test_model_correct_format = ExampleClass()
        test_model_correct_format.just_numbers = '1234566p3455pppp'
        test_model_correct_format.finalise_and_validate()


def test_email_validator():
    example = ExampleClass(just_numbers='1234')
    example.finalise_and_validate()

    with pytest.raises(ValidationException):
        example.email = 'some_mail'
        example.finalise_and_validate()

    example.email = 'acme@coppa.com'
    example.finalise_and_validate()


def test_min_max():
    example = ExampleClass(just_numbers='1234')
    example.finalise_and_validate()

    with pytest.raises(ValidationException):
        example.distance = 1
        example.finalise_and_validate()

    with pytest.raises(ValidationException):
        example.distance = 16
        example.finalise_and_validate()

    example.distance = 10
    example.finalise_and_validate()


def test_unique():
    example = ExampleClass(just_numbers='1234')
    example.finalise_and_validate()
    with pytest.raises(ValidationException):
        example.numbers = [1, 2, 1]
        example.finalise_and_validate()

    with pytest.raises(ValidationException):
        example.numbers = ['a', 'b', 'a']
        example.finalise_and_validate()

    example.numbers = ['a', 'b', 'c']
    example.finalise_and_validate()

    example.numbers = [1, 2, 3]
    example.finalise_and_validate()


def test_not_empty_validation():
    project = Project().update(name='')
    with pytest.raises(ValidationException):
        project.finalise_and_validate()
    project.update(name='some_name')
    project.finalise_and_validate()


def test_past_validation():
    project = Project().update(name='some project').append_to(
        tasks=Task().update(name='some task', description='some description'))
    project.tasks[0].complete()
    project.finalise_and_validate()
    print(('{}'.format(project)))
    project.tasks[0].update(closed_date=(datetime.datetime.now() - timedelta(days=1)))
    print(('\n\n> one day in the past \n{}'.format(project)))
    project.finalise_and_validate()

    with pytest.raises(ValidationException):
        project.tasks[0].update(closed_date=(datetime.datetime.now() + timedelta(days=1)))
        project.finalise_and_validate()

    with pytest.raises(ValidationException):
        project.tasks[0].update(closed_date='past')
        project.finalise_and_validate()


def test_future_validation():
    test_model = ExampleClass()
    test_model.just_numbers = 123
    test_model.finalise_and_validate()
    test_model.future_field = (datetime.datetime.now() + timedelta(days=1))
    test_model.finalise_and_validate()
    with pytest.raises(ValidationException):
        test_model.future_field = (datetime.datetime.now() - timedelta(days=1))
        print(('\n\n> one day in the in the future \n{}'.format(test_model)))
        test_model.finalise_and_validate()

    with pytest.raises(ValidationException):
        test_model.future_field = 'future'
        test_model.finalise_and_validate()


def test_validate_method():
    payment = Payment(method=PaymentMethod.MASTER, customer_id='123456', customer_secret='123')
    with pytest.raises(ValidationException):
        payment.finalise_and_validate()
    payment.customer_id = '1234567890123456'
    payment.finalise_and_validate()
