#!/usr/bin/env python3

"""
Smoke tests for tennis_game.html.

Validates HTML structure, question bank integrity, configuration
constants, and absence of external dependencies. Runs offline
with no browser required.
"""

# Standard Library
import os
import re
import json

# PIP3 modules
import pytest

# local repo modules
import git_file_utils

REPO_ROOT = git_file_utils.get_repo_root()
HTML_FILE = os.path.join(REPO_ROOT, "tennis_game.html")


#============================================
@pytest.fixture(scope="module")
def html_content() -> str:
	"""Read the full HTML file content once for all tests."""
	assert os.path.isfile(HTML_FILE), f"missing file: {HTML_FILE}"
	with open(HTML_FILE, "r", encoding="utf-8") as f:
		content = f.read()
	return content


#============================================
@pytest.fixture(scope="module")
def script_content(html_content: str) -> str:
	"""Extract the JavaScript between <script> tags."""
	match = re.search(r"<script>(.*?)</script>", html_content, re.DOTALL)
	assert match is not None, "no <script> block found in HTML"
	return match.group(1)


#============================================
@pytest.fixture(scope="module")
def questions(script_content: str) -> list:
	"""
	Extract the QUESTIONS array from the JS source and parse it.

	Uses per-object regex extraction to avoid issues with JS
	comments inside string values (e.g. '//' as a choice).
	"""
	# find the QUESTIONS array block
	match = re.search(
		r"const QUESTIONS\s*=\s*\[(.*?)\];",
		script_content,
		re.DOTALL,
	)
	assert match is not None, "QUESTIONS array not found in script"
	raw = match.group(1)

	# extract individual question objects using a pattern that
	# matches the known structure: { category: "...", ... answer: N }
	obj_pattern = re.compile(
		r'\{\s*category:\s*"([^"]+)"\s*,'
		r'\s*question:\s*"([^"]+)"\s*,'
		r'\s*choices:\s*\[([^\]]+)\]\s*,'
		r'\s*answer:\s*(\d+)\s*\}',
	)
	parsed = []
	for m in obj_pattern.finditer(raw):
		# parse the choices array from the captured group
		choices_raw = m.group(3)
		choices = re.findall(r'"([^"]*)"', choices_raw)
		question_obj = {
			"category": m.group(1),
			"question": m.group(2),
			"choices": choices,
			"answer": int(m.group(4)),
		}
		parsed.append(question_obj)
	assert len(parsed) > 0, "failed to parse any questions from QUESTIONS array"
	return parsed


#============================================
class TestHTMLStructure:
	"""Verify basic HTML document structure."""

	def test_file_exists(self) -> None:
		"""HTML file must exist at repo root."""
		assert os.path.isfile(HTML_FILE)

	def test_has_doctype(self, html_content: str) -> None:
		"""File must start with <!DOCTYPE html>."""
		assert html_content.strip().startswith("<!DOCTYPE html>")

	def test_has_canvas(self, html_content: str) -> None:
		"""Must contain a canvas element with id gameCanvas."""
		assert '<canvas id="gameCanvas">' in html_content

	def test_has_script_block(self, html_content: str) -> None:
		"""Must contain an inline script block."""
		assert "<script>" in html_content
		assert "</script>" in html_content

	def test_has_style_block(self, html_content: str) -> None:
		"""Must contain an inline style block."""
		assert "<style>" in html_content


#============================================
class TestNoExternalDependencies:
	"""Ensure the file is fully self-contained."""

	def test_no_external_scripts(self, html_content: str) -> None:
		"""No external script src attributes."""
		# match <script src="..."> but not inline <script>
		external_scripts = re.findall(r'<script\s+[^>]*src\s*=', html_content)
		assert len(external_scripts) == 0, (
			f"found external script tags: {external_scripts}"
		)

	def test_no_external_stylesheets(self, html_content: str) -> None:
		"""No external CSS link tags."""
		external_css = re.findall(
			r'<link\s+[^>]*rel\s*=\s*["\']stylesheet["\']', html_content
		)
		assert len(external_css) == 0, (
			f"found external stylesheet links: {external_css}"
		)

	def test_no_fetch_calls(self, script_content: str) -> None:
		"""No fetch() or XMLHttpRequest calls."""
		assert "fetch(" not in script_content, "found fetch() call"
		assert "XMLHttpRequest" not in script_content, (
			"found XMLHttpRequest usage"
		)


#============================================
class TestConfigurationConstants:
	"""Verify required global configuration constants are present."""

	REQUIRED_CONSTANTS = [
		"QUESTION_TIME_LIMIT",
		"CANVAS_WIDTH",
		"CANVAS_HEIGHT",
		"BALL_BASE_SPEED",
		"QUESTION_CHANCE",
		"SLOW_MOTION_FACTOR",
		"CPU_SKILL",
		"COURT_COLOR",
		"LINE_COLOR",
	]

	@pytest.mark.parametrize("const_name", REQUIRED_CONSTANTS)
	def test_constant_defined(self, script_content: str, const_name: str) -> None:
		"""Each required constant must be defined with const."""
		pattern = rf"const\s+{const_name}\s*="
		assert re.search(pattern, script_content), (
			f"constant {const_name} not found"
		)

	def test_canvas_width_is_1060(self, script_content: str) -> None:
		"""Canvas width should be 1060 (court 800 + scoreboard panel 260)."""
		match = re.search(r"const CANVAS_WIDTH\s*=\s*(\d+)", script_content)
		assert match is not None
		assert int(match.group(1)) == 1060

	def test_canvas_height_is_600(self, script_content: str) -> None:
		"""Canvas height should be 600."""
		match = re.search(r"const CANVAS_HEIGHT\s*=\s*(\d+)", script_content)
		assert match is not None
		assert int(match.group(1)) == 600

	def test_question_chance_valid_range(self, script_content: str) -> None:
		"""QUESTION_CHANCE must be between 0 and 1."""
		match = re.search(
			r"const QUESTION_CHANCE\s*=\s*([0-9.]+)", script_content
		)
		assert match is not None
		value = float(match.group(1))
		assert 0.0 <= value <= 1.0, f"QUESTION_CHANCE={value} out of range"


#============================================
class TestQuestionBank:
	"""Validate the integrity of the embedded question bank."""

	EXPECTED_CATEGORIES = {"Python", "JavaScript", "HTML/CSS", "SQL", "General"}

	def test_minimum_question_count(self, questions: list) -> None:
		"""Must have at least 40 questions."""
		assert len(questions) >= 40, (
			f"only {len(questions)} questions, need at least 40"
		)

	def test_each_question_has_required_fields(self, questions: list) -> None:
		"""Every question must have category, question, choices, answer."""
		required_keys = {"category", "question", "choices", "answer"}
		for i, q in enumerate(questions):
			missing = required_keys - set(q.keys())
			assert not missing, (
				f"question {i} missing fields: {missing}"
			)

	def test_each_question_has_four_choices(self, questions: list) -> None:
		"""Every question must have exactly 4 choices."""
		for i, q in enumerate(questions):
			assert len(q["choices"]) == 4, (
				f"question {i} has {len(q['choices'])} choices, expected 4"
			)

	def test_answer_index_in_bounds(self, questions: list) -> None:
		"""Answer index must be 0, 1, 2, or 3."""
		for i, q in enumerate(questions):
			assert 0 <= q["answer"] <= 3, (
				f"question {i} answer index {q['answer']} out of range"
			)

	def test_all_categories_present(self, questions: list) -> None:
		"""All expected categories must appear."""
		found_categories = {q["category"] for q in questions}
		missing = self.EXPECTED_CATEGORIES - found_categories
		assert not missing, f"missing categories: {missing}"

	def test_no_duplicate_questions(self, questions: list) -> None:
		"""No two questions should have identical text."""
		texts = [q["question"] for q in questions]
		duplicates = [t for t in texts if texts.count(t) > 1]
		assert not duplicates, (
			f"duplicate question texts: {set(duplicates)}"
		)

	def test_no_empty_question_text(self, questions: list) -> None:
		"""Question text must not be empty."""
		for i, q in enumerate(questions):
			assert q["question"].strip(), (
				f"question {i} has empty question text"
			)

	def test_no_empty_choices(self, questions: list) -> None:
		"""No choice string should be empty."""
		for i, q in enumerate(questions):
			for j, choice in enumerate(q["choices"]):
				assert choice.strip(), (
					f"question {i} choice {j} is empty"
				)

	def test_answer_differs_from_wrong_choices(self, questions: list) -> None:
		"""The correct answer should not be identical to another choice."""
		for i, q in enumerate(questions):
			correct_text = q["choices"][q["answer"]]
			for j, choice in enumerate(q["choices"]):
				if j != q["answer"]:
					assert choice != correct_text, (
						f"question {i}: choice {j} duplicates the answer"
					)

	def test_python_question_count(self, questions: list) -> None:
		"""Should have at least 10 Python questions."""
		count = sum(1 for q in questions if q["category"] == "Python")
		assert count >= 10, f"only {count} Python questions"

	def test_javascript_question_count(self, questions: list) -> None:
		"""Should have at least 8 JavaScript questions."""
		count = sum(1 for q in questions if q["category"] == "JavaScript")
		assert count >= 8, f"only {count} JavaScript questions"


#============================================
class TestGameStates:
	"""Verify the game state machine has required states."""

	REQUIRED_STATES = [
		"TITLE",
		"SERVING",
		"BALL_TO_CPU",
		"BALL_TO_PLAYER",
		"QUESTION_TIME",
		"POINT_SCORED",
		"GAME_OVER",
	]

	@pytest.mark.parametrize("state_name", REQUIRED_STATES)
	def test_state_defined(self, script_content: str, state_name: str) -> None:
		"""Each required state must exist in the STATES object."""
		assert state_name in script_content, (
			f"state {state_name} not found"
		)


#============================================
class TestGameFunctions:
	"""Verify essential game functions are defined."""

	REQUIRED_FUNCTIONS = [
		"projectToScreen",
		"drawCourt",
		"drawBall",
		"drawPlayerRacket",
		"drawCPURacket",
		"drawScoreboard",
		"drawQuestionOverlay",
		"drawTitleScreen",
		"updateBall",
		"updateCPU",
		"serveBall",
		"awardPoint",
		"awardGame",
		"awardSet",
		"handleAnswer",
		"gameLoop",
		"shuffleQuestions",
	]

	@pytest.mark.parametrize("func_name", REQUIRED_FUNCTIONS)
	def test_function_defined(self, script_content: str, func_name: str) -> None:
		"""Each required function must be defined."""
		pattern = rf"function\s+{func_name}\s*\("
		assert re.search(pattern, script_content), (
			f"function {func_name}() not found"
		)


#============================================
class TestScoringLogic:
	"""Verify scoring-related patterns in the code."""

	def test_tennis_point_values(self, script_content: str) -> None:
		"""Score display should include standard tennis points."""
		for value in ["0", "15", "30", "40"]:
			assert f'"{value}"' in script_content, (
				f"point value {value} not found in score display"
			)

	def test_deuce_handling(self, script_content: str) -> None:
		"""Must handle advantage/deuce with AD display."""
		assert '"AD"' in script_content, "advantage display not found"

	def test_tiebreak_support(self, script_content: str) -> None:
		"""Must have tiebreak logic."""
		assert "tiebreak" in script_content.lower(), (
			"tiebreak logic not found"
		)

	def test_best_of_three_sets(self, script_content: str) -> None:
		"""Match should end at 2 sets won."""
		assert "playerSets >= 2" in script_content, (
			"best-of-3 check for player not found"
		)
		assert "cpuSets >= 2" in script_content, (
			"best-of-3 check for CPU not found"
		)
