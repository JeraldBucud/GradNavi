"""
Deterministic WBS 7.2 Job Description Matching.

The service treats job-description text as untrusted input.

Matching uses existing GradNavi canonical Skill records and
SkillAlias records. It does not call a generative AI provider and
does not modify Career Recommendation, Skill Gap, or Career
Readiness scores.
"""

from dataclasses import dataclass
import re
import unicodedata

from careers.models import SkillAlias
from profiles.models import (
    Skill,
    StudentProfile,
    StudentSkill,
)


MATCH_SOURCE_CANONICAL = "canonical"
MATCH_SOURCE_ALIAS = "alias"


@dataclass(frozen=True)
class JobRequirementMatch:
    """
    One canonical GradNavi requirement extracted from job text.
    """

    skill_id: int
    skill_name: str
    concept_type: str
    matched_term: str
    match_source: str
    current_proficiency: str | None


@dataclass(frozen=True)
class JobDescriptionMatchResult:
    """
    Deterministic comparison between one job description and
    one authenticated Student Profile.
    """

    matched_requirements: tuple[
        JobRequirementMatch,
        ...,
    ]

    missing_requirements: tuple[
        JobRequirementMatch,
        ...,
    ]


    @property
    def matched_requirement_count(self):
        return len(
            self.matched_requirements
        )


    @property
    def missing_requirement_count(self):
        return len(
            self.missing_requirements
        )


    @property
    def total_requirement_count(self):
        return (
            self.matched_requirement_count
            + self.missing_requirement_count
        )


    @property
    def canonical_match_count(self):
        return sum(
            requirement.match_source
            == MATCH_SOURCE_CANONICAL
            for requirement in (
                self.matched_requirements
                + self.missing_requirements
            )
        )


    @property
    def alias_match_count(self):
        return sum(
            requirement.match_source
            == MATCH_SOURCE_ALIAS
            for requirement in (
                self.matched_requirements
                + self.missing_requirements
            )
        )


def _normalise_match_text(value):
    """
    Unicode-normalise and case-fold text while preserving punctuation
    used by technology names such as C++, C#, .NET, and Node.js.
    """

    normalised = unicodedata.normalize(
        "NFKC",
        value,
    )

    normalised = normalised.casefold()

    return re.sub(
        r"\s+",
        " ",
        normalised,
    ).strip()


def _is_word_character(character):
    return (
        character.isalnum()
        or character == "_"
    )


def _find_term_index(
    text,
    term,
    *,
    start=0,
):
    """
    Find a complete deterministic term occurrence.

    Alphanumeric edges require token boundaries. Punctuation remains
    significant so technology labels are not reduced to generic words.
    """

    normalised_term = (
        _normalise_match_text(
            term
        )
    )

    if not normalised_term:
        return None

    while True:
        index = text.find(
            normalised_term,
            start,
        )

        if index < 0:
            return None

        end = (
            index
            + len(
                normalised_term
            )
        )

        left_requires_boundary = (
            _is_word_character(
                normalised_term[0]
            )
        )

        right_requires_boundary = (
            _is_word_character(
                normalised_term[-1]
            )
        )

        left_ok = (
            not left_requires_boundary
            or index == 0
            or not _is_word_character(
                text[
                    index - 1
                ]
            )
        )

        right_ok = (
            not right_requires_boundary
            or end == len(text)
            or not _is_word_character(
                text[end]
            )
        )

        if left_ok and right_ok:
            return index

        start = index + 1


def _requires_explicit_knowledge_context(
    *,
    term,
    concept_type,
):
    """
    Generic single-word knowledge concepts need clear requirement
    wording before they are treated as job requirements.

    This prevents verbs such as "design features" from being
    interpreted as the canonical knowledge concept "Design".
    """

    return (
        concept_type == "knowledge"
        and len(
            term.split()
        ) == 1
    )


def _has_explicit_knowledge_context(
    *,
    text,
    term,
    index,
):
    """
    Accept conservative noun-style requirement wording.

    Examples:
    - knowledge of Design
    - experience with Design
    - proficiency in Design
    - familiarity with Design
    - Design skills
    - Design knowledge
    """

    end = (
        index
        + len(term)
    )

    before = text[
        max(
            0,
            index - 80,
        ):
        index
    ]

    after = text[
        end:
        min(
            len(text),
            end + 80,
        )
    ]

    prefix_patterns = (
        r"\bknowledge\s+of\s*$",
        r"\bunderstanding\s+of\s*$",
        r"\bexperience\s+(?:with|in)\s*$",
        r"\bproficiency\s+(?:with|in)\s*$",
        r"\bfamiliarity\s+with\s*$",
        r"\bskills?\s+(?:with|in)\s*$",
    )

    suffix_patterns = (
        r"^\s+(?:knowledge|skills?|experience|proficiency)\b",
    )

    return (
        any(
            re.search(
                pattern,
                before,
            )
            for pattern
            in prefix_patterns
        )
        or any(
            re.search(
                pattern,
                after,
            )
            for pattern
            in suffix_patterns
        )
    )


def _find_requirement_index(
    *,
    text,
    term,
    concept_type,
):
    """
    Find the first acceptable occurrence of a canonical or alias term.

    Most concepts use exact deterministic term matching.

    Generic single-word knowledge concepts require explicit
    requirement context to reduce false positives.
    """

    search_start = 0

    while True:
        index = _find_term_index(
            text,
            term,
            start=search_start,
        )

        if index is None:
            return None

        if not (
            _requires_explicit_knowledge_context(
                term=term,
                concept_type=(
                    concept_type
                ),
            )
        ):
            return index

        if (
            _has_explicit_knowledge_context(
                text=text,
                term=term,
                index=index,
            )
        ):
            return index

        search_start = (
            index + 1
        )


def _load_canonical_vocabulary():
    groups = {}

    rows = (
        Skill.objects
        .order_by(
            "id",
        )
        .values(
            "id",
            "name",
            "concept_type",
        )
    )

    for row in rows:
        term = _normalise_match_text(
            row["name"]
        )

        if not term:
            continue

        groups.setdefault(
            term,
            [],
        ).append(row)

    return groups


def _load_alias_vocabulary():
    groups = {}

    rows = (
        SkillAlias.objects
        .select_related(
            "skill",
        )
        .order_by(
            "alias",
            "skill_id",
        )
        .values(
            "alias",
            "skill_id",
            "skill__name",
            "skill__concept_type",
        )
    )

    for row in rows:
        term = _normalise_match_text(
            row["alias"]
        )

        if not term:
            continue

        groups.setdefault(
            term,
            [],
        ).append(row)

    return groups


def extract_job_requirements(
    job_description,
):
    """
    Extract canonical GradNavi concepts from one job description.

    Exact canonical labels receive priority over aliases.

    Ambiguous canonical or alias labels are skipped rather than
    guessing which Skill record the text refers to.
    """

    text = _normalise_match_text(
        job_description
    )

    canonical_groups = (
        _load_canonical_vocabulary()
    )

    alias_groups = (
        _load_alias_vocabulary()
    )

    extracted = {}


    for term in sorted(
        canonical_groups,
        key=lambda value: (
            -len(value),
            value,
        ),
    ):
        rows = canonical_groups[term]

        skill_ids = {
            row["id"]
            for row in rows
        }

        if len(skill_ids) != 1:
            continue

        row = rows[0]

        index = _find_requirement_index(
            text=text,
            term=term,
            concept_type=(
                row[
                    "concept_type"
                ]
            ),
        )

        if index is None:
            continue

        extracted[
            row["id"]
        ] = (
            index,
            JobRequirementMatch(
                skill_id=row["id"],
                skill_name=(
                    row["name"]
                ),
                concept_type=(
                    row[
                        "concept_type"
                    ]
                ),
                matched_term=(
                    row["name"]
                ),
                match_source=(
                    MATCH_SOURCE_CANONICAL
                ),
                current_proficiency=None,
            ),
        )


    for term in sorted(
        alias_groups,
        key=lambda value: (
            -len(value),
            value,
        ),
    ):
        rows = alias_groups[term]

        skill_ids = {
            row["skill_id"]
            for row in rows
        }

        if len(skill_ids) != 1:
            continue

        row = rows[0]

        skill_id = row[
            "skill_id"
        ]

        if skill_id in extracted:
            continue

        canonical_rows = (
            canonical_groups.get(
                term,
                [],
            )
        )

        canonical_skill_ids = {
            canonical_row["id"]
            for canonical_row
            in canonical_rows
        }

        if (
            canonical_skill_ids
            and canonical_skill_ids
            != {skill_id}
        ):
            continue

        index = _find_requirement_index(
            text=text,
            term=term,
            concept_type=(
                row[
                    "skill__concept_type"
                ]
            ),
        )

        if index is None:
            continue

        extracted[
            skill_id
        ] = (
            index,
            JobRequirementMatch(
                skill_id=skill_id,
                skill_name=(
                    row[
                        "skill__name"
                    ]
                ),
                concept_type=(
                    row[
                        "skill__concept_type"
                    ]
                ),
                matched_term=(
                    row["alias"]
                ),
                match_source=(
                    MATCH_SOURCE_ALIAS
                ),
                current_proficiency=None,
            ),
        )


    ordered = sorted(
        extracted.values(),
        key=lambda item: (
            item[0],
            item[1]
            .skill_name
            .casefold(),
            item[1].skill_id,
        ),
    )

    return tuple(
        requirement
        for _index, requirement
        in ordered
    )


def match_job_description(
    *,
    student_profile,
    job_description,
):
    """
    Compare extracted requirements only with the authenticated
    Student Profile supplied by the API layer.
    """

    if not isinstance(
        student_profile,
        StudentProfile,
    ):
        raise TypeError(
            "student_profile must be "
            "a StudentProfile instance."
        )

    extracted = (
        extract_job_requirements(
            job_description
        )
    )

    proficiencies = dict(
        StudentSkill.objects
        .filter(
            student_profile=(
                student_profile
            ),
        )
        .values_list(
            "skill_id",
            "proficiency_level",
        )
    )

    matched = []

    missing = []

    for requirement in extracted:
        proficiency = (
            proficiencies.get(
                requirement.skill_id
            )
        )

        compared = (
            JobRequirementMatch(
                skill_id=(
                    requirement.skill_id
                ),
                skill_name=(
                    requirement.skill_name
                ),
                concept_type=(
                    requirement.concept_type
                ),
                matched_term=(
                    requirement.matched_term
                ),
                match_source=(
                    requirement.match_source
                ),
                current_proficiency=(
                    proficiency
                ),
            )
        )

        if proficiency is None:
            missing.append(
                compared
            )
        else:
            matched.append(
                compared
            )

    return JobDescriptionMatchResult(
        matched_requirements=tuple(
            matched
        ),
        missing_requirements=tuple(
            missing
        ),
    )
