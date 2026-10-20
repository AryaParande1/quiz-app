// Quiz App - Interactive Client Engine

let questions = [];
let currentIndex = 0;
let userAnswers = {};
let timerInterval = null;
let timeLeft = 20;
const QUESTION_TIME_LIMIT = 20;

// DOM Elements
const loadingView = document.getElementById('loadingView');
const startView = document.getElementById('startView');
const quizView = document.getElementById('quizView');
const resultsView = document.getElementById('resultsView');

const startBtn = document.getElementById('startBtn');
const nextBtn = document.getElementById('nextBtn');
const restartBtn = document.getElementById('restartBtn');

const qTracker = document.getElementById('qTracker');
const timerDisplay = document.getElementById('timerDisplay');
const progressBar = document.getElementById('progressBar');
const qCategory = document.getElementById('qCategory');
const qText = document.getElementById('qText');
const optionsContainer = document.getElementById('optionsContainer');
const feedbackNotice = document.getElementById('feedbackNotice');

// Results elements
const scoreNum = document.getElementById('scoreNum');
const percentNum = document.getElementById('percentNum');
const badgeRank = document.getElementById('badgeRank');
const badgeContainer = document.getElementById('badgeContainer');
const reviewList = document.getElementById('reviewList');

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
  await fetchQuestions();
  startBtn.addEventListener('click', startQuiz);
  nextBtn.addEventListener('click', handleNext);
  restartBtn.addEventListener('click', restartQuiz);
});

async function fetchQuestions() {
  try {
    const res = await fetch('/api/questions');
    const data = await res.json();
    questions = data.questions || [];
    loadingView.classList.add('hidden');
    startView.classList.remove('hidden');
  } catch (err) {
    loadingView.innerHTML = `<p style="color: #ef4444;">Failed to load questions. Ensure backend is running.</p>`;
  }
}

function startQuiz() {
  currentIndex = 0;
  userAnswers = {};
  startView.classList.add('hidden');
  resultsView.classList.add('hidden');
  quizView.classList.remove('hidden');
  renderCurrentQuestion();
}

function renderCurrentQuestion() {
  clearInterval(timerInterval);
  feedbackNotice.classList.add('hidden');
  nextBtn.disabled = true;

  if (currentIndex >= questions.length) {
    submitQuiz();
    return;
  }

  const q = questions[currentIndex];
  qTracker.textContent = `Question ${currentIndex + 1} / ${questions.length}`;
  qCategory.textContent = q.category;
  qText.textContent = q.question;

  // Progress Bar
  const progressPercent = ((currentIndex + 1) / questions.length) * 100;
  progressBar.style.width = `${progressPercent}%`;

  // Options
  optionsContainer.innerHTML = '';
  const optionKeys = ['A', 'B', 'C', 'D'];

  q.options.forEach((opt, idx) => {
    const btn = document.createElement('button');
    btn.className = 'option-btn';
    btn.innerHTML = `
      <span class="option-key">${optionKeys[idx] || idx + 1}</span>
      <span>${opt}</span>
    `;
    btn.addEventListener('click', () => selectOption(idx, btn));
    optionsContainer.appendChild(btn);
  });

  // Start Timer
  startTimer();
}

function startTimer() {
  timeLeft = QUESTION_TIME_LIMIT;
  timerDisplay.textContent = `${timeLeft}s`;

  timerInterval = setInterval(() => {
    timeLeft--;
    timerDisplay.textContent = `${timeLeft}s`;

    if (timeLeft <= 5) {
      timerDisplay.style.color = '#ef4444';
    } else {
      timerDisplay.style.color = '#fbbf24';
    }

    if (timeLeft <= 0) {
      clearInterval(timerInterval);
      // Auto move if no selection made
      if (userAnswers[questions[currentIndex].id] === undefined) {
        userAnswers[questions[currentIndex].id] = -1; // timed out
      }
      disableOptions();
      nextBtn.disabled = false;
      feedbackNotice.textContent = "⏱️ Time's up for this question!";
      feedbackNotice.classList.remove('hidden');
    }
  }, 1000);
}

function selectOption(selectedIndex, btnElement) {
  clearInterval(timerInterval);
  const q = questions[currentIndex];
  userAnswers[q.id] = selectedIndex;

  const allBtns = optionsContainer.querySelectorAll('.option-btn');
  allBtns.forEach(b => b.classList.remove('selected'));
  btnElement.classList.add('selected');

  disableOptions();
  nextBtn.disabled = false;
}

function disableOptions() {
  const allBtns = optionsContainer.querySelectorAll('.option-btn');
  allBtns.forEach(b => b.disabled = true);
}

function handleNext() {
  currentIndex++;
  if (currentIndex < questions.length) {
    renderCurrentQuestion();
  } else {
    submitQuiz();
  }
}

async function submitQuiz() {
  clearInterval(timerInterval);
  quizView.classList.add('hidden');
  loadingView.classList.remove('hidden');

  try {
    const res = await fetch('/api/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answers: userAnswers })
    });
    const result = await res.json();
    displayResults(result);
  } catch (err) {
    alert('Error submitting answers. Please check backend connection.');
  } finally {
    loadingView.classList.add('hidden');
  }
}

function displayResults(data) {
  resultsView.classList.remove('hidden');
  scoreNum.textContent = `${data.score} / ${data.total}`;
  percentNum.textContent = `${data.percentage}%`;
  badgeRank.textContent = data.badge;

  // Render question review
  reviewList.innerHTML = '';
  data.results.forEach((item, index) => {
    const div = document.createElement('div');
    div.className = `review-item ${item.is_correct ? 'pass' : 'fail'}`;
    const statusIcon = item.is_correct ? '✅' : '❌';
    div.innerHTML = `
      <div>
        <strong>Q${index + 1}: ${item.question.slice(0, 48)}...</strong>
        <p style="color: #94a3b8; font-size: 0.78rem; margin-top: 4px;">${item.explanation}</p>
      </div>
      <span>${statusIcon}</span>
    `;
    reviewList.appendChild(div);
  });
}

function restartQuiz() {
  resultsView.classList.add('hidden');
  startView.classList.remove('hidden');
}
