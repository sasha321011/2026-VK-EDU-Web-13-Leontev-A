import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.db import transaction
from faker import Faker

from questions.models import Question, Answer, Tag, QuestionLike, AnswerLike
from core.models import Profile

fake = Faker('ru_RU')


class Command(BaseCommand):
    help = 'Заполняет БД тестовыми данными'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int)

    @transaction.atomic
    def handle(self, *args, **options):
        ratio = options['ratio']

        n_users = ratio
        n_questions = ratio * 10
        n_answers = ratio * 100
        n_tags = ratio
        n_likes = ratio * 200

        self.stdout.write(f'Users: {n_users}, Questions: {n_questions}, '
                          f'Answers: {n_answers}, Tags: {n_tags}, Likes: {n_likes}')

        pwd = make_password('password123')
        users = [User(username=f'user{i}', password=pwd) for i in range(n_users)]
        User.objects.bulk_create(users, batch_size=1000)

        profiles = [Profile(user=u) for u in users]
        Profile.objects.bulk_create(profiles, batch_size=1000)

        tags = [Tag(name=f'tag{i}') for i in range(n_tags)]
        Tag.objects.bulk_create(tags, batch_size=1000)

        questions = [
            Question(author=random.choice(users),
                     title=fake.sentence(nb_words=6),
                     text=fake.paragraph())
            for _ in range(n_questions)
        ]
        Question.objects.bulk_create(questions, batch_size=1000)

        QuestionTag = Question.tags.through
        pairs = set()
        target = min(n_questions * 2, n_questions * n_tags)
        while len(pairs) < target:
            pairs.add((random.choice(questions).id, random.choice(tags).id))
        QuestionTag.objects.bulk_create(
            [QuestionTag(question_id=q, tag_id=t) for q, t in pairs],
            batch_size=1000
        )

        answers = [
            Answer(question=random.choice(questions),
                   author=random.choice(users),
                   text=fake.paragraph())
            for _ in range(n_answers)
        ]
        Answer.objects.bulk_create(answers, batch_size=1000)

        q_pairs = set()
        q_target = n_likes // 2
        while len(q_pairs) < q_target:
            q_pairs.add((random.choice(users).id, random.choice(questions).id))
        QuestionLike.objects.bulk_create(
            [QuestionLike(user_id=u, question_id=q, value=random.choice([1, -1]))
             for u, q in q_pairs],
            batch_size=1000
        )

        a_pairs = set()
        a_target = n_likes // 2
        while len(a_pairs) < a_target:
            a_pairs.add((random.choice(users).id, random.choice(answers).id))
        AnswerLike.objects.bulk_create(
            [AnswerLike(user_id=u, answer_id=a, value=random.choice([1, -1]))
             for u, a in a_pairs],
            batch_size=1000
        )

        self.stdout.write(self.style.SUCCESS('БД заполнена'))