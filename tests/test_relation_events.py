import os
import unittest
from unittest.mock import patch

from scripts.cat.cats import Cat
from scripts.cat_relations.relationship import Relationship
from scripts.clan import Clan
from scripts.events_module.relationship.pregnancy_events import Pregnancy_Events
from scripts.events_module.relationship.romantic_events import Romantic_Events

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"


class CanHaveCubs(unittest.TestCase):
    def test_prevent_cubs(self):
        # given
        cat = Cat()
        cat.no_cubs = True

        # then
        self.assertFalse(Pregnancy_Events.check_if_can_have_cubs(cat, single_parentage=True, allow_affair=True))

    @patch('scripts.events_module.relationship.pregnancy_events.Pregnancy_Events.check_if_can_have_cubs')
    def test_no_cub_setting(self, check_if_can_have_cubs):
        # given
        test_clan = Clan(name="clan")
        test_clan.pregnancy_data = {}
        cat1 = Cat(gender='female')
        cat1.no_cubs = True
        cat2 = Cat(gender='male')

        cat1.mate.append(cat2.ID)
        cat2.mate.append(cat1.ID)
        relation1 = Relationship(cat1, cat2, mates=True, family=False, romantic_love=100)
        relation2 = Relationship(cat2, cat1, mates=True, family=False, romantic_love=100)
        cat1.relationships[cat2.ID] = relation1
        cat2.relationships[cat1.ID] = relation2

        # when
        check_if_can_have_cubs.return_value = True
        Pregnancy_Events.handle_having_cubs(cat=cat1, clan=test_clan)

        # then
        self.assertNotIn(cat1.ID, test_clan.pregnancy_data.keys())


class SameSexAdoptions(unittest.TestCase):
    def test_cubs_are_adopted(self):
        # given

        cat1 = Cat(gender='female', age="adult", moons=40)
        cat2 = Cat(gender='female', age="adult", moons=40)
        cat1.mate.append(cat2.ID)
        cat2.mate.append(cat1.ID)

        # when
        single_parentage = False
        allow_affair = False
        self.assertTrue(Pregnancy_Events.check_if_can_have_cubs(cat1, single_parentage, allow_affair))
        self.assertTrue(Pregnancy_Events.check_if_can_have_cubs(cat2, single_parentage, allow_affair))

        can_have_cubs, cubs_are_adopted = Pregnancy_Events.check_second_parent(
            cat=cat1,
            second_parent=cat2,
            single_parentage=single_parentage,
            allow_affair=allow_affair,
            same_sex_birth=False,
            same_sex_adoption=True
        )
        self.assertTrue(can_have_cubs)
        self.assertTrue(cubs_are_adopted)


class Pregnancy(unittest.TestCase):
    @patch('scripts.events_module.relationship.pregnancy_events.Pregnancy_Events.check_if_can_have_cubs')
    def test_single_cat_female(self, check_if_can_have_cubs):
        # given
        clan = Clan(name="clan")
        cat = Cat(gender='female', age="adult", moons=40)
        clan.pregnancy_data = {}

        # when
        check_if_can_have_cubs.return_value = True
        Pregnancy_Events.handle_zero_moon_pregnant(cat, None, clan)

        # then
        self.assertIn(cat.ID, clan.pregnancy_data.keys())

    @patch('scripts.events_module.relationship.pregnancy_events.Pregnancy_Events.check_if_can_have_cubs')
    def test_pair(self, check_if_can_have_cubs):
        # given
        clan = Clan(name="clan")
        cat1 = Cat(gender='female', age="adult", moons=40)
        cat2 = Cat(gender='male', age="adult", moons=40)

        clan.pregnancy_data = {}

        # when
        check_if_can_have_cubs.return_value = True
        Pregnancy_Events.handle_zero_moon_pregnant(cat1, cat2, clan)

        # then
        self.assertIn(cat1.ID, clan.pregnancy_data.keys())
        self.assertEqual(clan.pregnancy_data[cat1.ID]["second_parent"], cat2.ID)


class Mates(unittest.TestCase):
    def test_platonic_cub_mating(self):
        # given
        cat1 = Cat(moons=3)
        cat2 = Cat(moons=3)

        relationship1 = Relationship(cat1, cat2)
        relationship2 = Relationship(cat2, cat1)
        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.ID] = relationship1
        cat2.relationships[cat1.ID] = relationship2

        # when
        relationship1.platonic_like = 100
        relationship2.platonic_like = 100

        # then
        self.assertFalse(Romantic_Events.check_if_new_mate(cat1, cat2)[0])

    def test_platonic_apprentice_mating(self):
        # given
        cat1 = Cat(moons=6)
        cat2 = Cat(moons=6)

        relationship1 = Relationship(cat1, cat2)
        relationship2 = Relationship(cat2, cat1)
        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.ID] = relationship1
        cat2.relationships[cat1.ID] = relationship2

        # when
        relationship1.platonic_like = 100
        relationship2.platonic_like = 100

        # then
        self.assertFalse(Romantic_Events.check_if_new_mate(cat1, cat2)[0])

    def test_romantic_cub_mating(self):
        # given
        cat1 = Cat(moons=3)
        cat2 = Cat(moons=3)

        relationship1 = Relationship(cat1, cat2)
        relationship2 = Relationship(cat2, cat1)
        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.ID] = relationship1
        cat2.relationships[cat1.ID] = relationship2

        # when
        relationship1.romantic_love = 100
        relationship2.romantic_love = 100

        # then
        self.assertFalse(Romantic_Events.check_if_new_mate(cat1, cat2)[0])

    def test_romantic_apprentice_mating(self):
        # given
        cat1 = Cat(moons=6)
        cat2 = Cat(moons=6)

        relationship1 = Relationship(cat1, cat2)
        relationship2 = Relationship(cat2, cat1)
        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.ID] = relationship1
        cat2.relationships[cat1.ID] = relationship2

        # when
        relationship1.romantic_love = 100
        relationship2.romantic_love = 100

        # then
        self.assertFalse(Romantic_Events.check_if_new_mate(cat1, cat2)[0])
