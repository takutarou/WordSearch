let inputCount = 1;
const maxInputs = 100;
let currentSearchId = null;

$(document).ready(function() {
    loadFileCount();

    // Enter key to submit search
    $(document).on('keypress', 'input[name^="word-"]', function(e) {
        if (e.which === 13) {
            executeSearch();
        }
    });
});

/**
 * Load file count from API
 */
function loadFileCount() {
    $.ajax({
        url: '/api/files',
        method: 'GET',
        success: function(response) {
            const fileCount = response.files ? response.files.length : 0;
            $('#file-count').text(fileCount + '件');
        },
        error: function(xhr, status, error) {
            console.error('Failed to load file count:', error);
            $('#file-count').text('--');
        }
    });
}

/**
 * Add a new search input field
 */
function addSearchInput() {
    if (inputCount >= maxInputs) {
        alert('検索欄は最大100個までです');
        return;
    }

    inputCount++;

    const inputHtml = `
        <div class="search-input-row" id="input-${inputCount}">
            <label for="word-${inputCount}">検索単語 ${inputCount}:</label>
            <input type="text"
                   id="word-${inputCount}"
                   name="word-${inputCount}"
                   maxlength="200"
                   placeholder="検索したい単語を入力"
                   aria-label="検索単語 ${inputCount}">
            <button class="btn btn-remove"
                    onclick="removeSearchInput(${inputCount})"
                    aria-label="検索欄 ${inputCount} を削除">
                -
            </button>
        </div>
    `;

    $('#search-inputs').append(inputHtml);
}

/**
 * Remove a search input field
 * @param {number} id - Input field ID to remove
 */
function removeSearchInput(id) {
    $(`#input-${id}`).remove();
    inputCount--;
}

/**
 * Validate input words
 * @param {Array<string>} words - Words to validate
 * @returns {Object} Validation result
 */
function validateWords(words) {
    if (words.length === 0) {
        return {
            valid: false,
            message: '検索単語を入力してください'
        };
    }

    for (let word of words) {
        if (word.length > 200) {
            return {
                valid: false,
                message: '検索単語は200文字以内で入力してください'
            };
        }
    }

    return { valid: true };
}

/**
 * Execute search
 */
function executeSearch() {
    // Collect words from all input fields
    const words = [];
    $('input[name^="word-"]').each(function() {
        const val = $(this).val().trim();
        if (val !== '') {
            words.push(val);
        }
    });

    // Validate
    const validation = validateWords(words);
    if (!validation.valid) {
        showError(validation.message);
        return;
    }

    // Hide error message
    hideError();

    // Show loading, hide results
    $('#loading').show();
    $('#results').hide();
    $('#search-button').prop('disabled', true);

    // Make API request
    $.ajax({
        url: '/api/search',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ words: words }),
        success: function(response) {
            const data = response.data || response;
            currentSearchId = data.search_id;
            displayResults(data);
            $('#loading').hide();
            $('#results').show();
            $('#search-button').prop('disabled', false);
        },
        error: function(xhr, status, error) {
            let errorMessage = '検索処理中にエラーが発生しました';

            if (xhr.responseJSON && xhr.responseJSON.error) {
                errorMessage = xhr.responseJSON.error;
            } else if (xhr.status === 0) {
                errorMessage = 'サーバーに接続できませんでした';
            }

            showError(errorMessage);
            $('#loading').hide();
            $('#search-button').prop('disabled', false);
        }
    });
}

/**
 * Display search results
 * @param {Object} response - API response object
 */
function displayResults(response) {
    // Display metadata
    $('#search-id').text(response.search_id || '--');
    $('#search-timestamp').text(response.timestamp || '--');

    // Clear previous results
    $('#results-list').empty();

    // Convert results object to array format
    const resultsArray = [];
    if (response.results && typeof response.results === 'object') {
        for (const word in response.results) {
            const wordResult = response.results[word];
            resultsArray.push({
                word: word,
                found: wordResult.hits_found,
                hit_files: wordResult.results ? wordResult.results.map(r => ({
                    filename: r.filename || r.file,
                    hit_count: r.hits,
                    highlighted_path: r.highlighted_relative
                })) : []
            });
        }
    }

    // Display each result
    if (resultsArray.length > 0) {
        resultsArray.forEach(function(result) {
            const cardHtml = createResultCard(result);
            $('#results-list').append(cardHtml);
        });
    } else {
        $('#results-list').append('<p>検索結果がありません</p>');
    }

    // Update certificate download link
    if (response.search_id) {
        $('#download-certificate').attr('href', '/api/certificate/' + response.search_id);
        $('#view-certificate').attr('href', '/certificate/' + response.search_id);
    }
}

/**
 * Create result card HTML
 * @param {Object} result - Single word search result
 * @returns {string} HTML string
 */
function createResultCard(result) {
    // Count files with actual hits (hit_count > 0)
    const filesWithHits = result.hit_files ? result.hit_files.filter(f => f.hit_count > 0).length : 0;
    const isHit = filesWithHits > 0;
    const cardClass = isHit ? 'hit' : 'no-hit';
    const badgeClass = isHit ? 'badge-hit' : 'badge-no-hit';
    const badgeText = isHit ? `ヒット: ${filesWithHits}件` : '非ヒット';

    let fileListHtml = '';
    if (result.hit_files && result.hit_files.length > 0) {
        fileListHtml = '<div class="file-list">';
        fileListHtml += '<div class="file-list-title">ファイル:</div>';

        result.hit_files.forEach(function(file) {
            const hitCount = file.hit_count || 0;
            const viewPath = file.highlighted_path || file.filename;

            // Show link only if there are hits
            const linkHtml = hitCount > 0 ? `
                <a href="/view/${encodeURIComponent(viewPath)}"
                   class="file-link"
                   target="_blank">
                    表示
                </a>
            ` : '';

            fileListHtml += `
                <div class="file-item">
                    <div>
                        <span class="file-name">${escapeHtml(file.filename)}</span>
                        <span class="file-count">(${hitCount}箇所)</span>
                    </div>
                    ${linkHtml}
                </div>
            `;
        });

        fileListHtml += '</div>';
    }

    const cardHtml = `
        <div class="result-card ${cardClass}">
            <div class="result-card-header">
                <div class="result-word">"${escapeHtml(result.word)}"</div>
                <span class="badge ${badgeClass}">${badgeText}</span>
            </div>
            ${fileListHtml}
        </div>
    `;

    return cardHtml;
}

/**
 * Show error message
 * @param {string} message - Error message to display
 */
function showError(message) {
    $('#error-message').text(message).addClass('show');

    // Scroll to error message
    $('html, body').animate({
        scrollTop: $('#error-message').offset().top - 100
    }, 300);
}

/**
 * Hide error message
 */
function hideError() {
    $('#error-message').removeClass('show');
}

/**
 * Escape HTML to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, function(m) { return map[m]; });
}

/**
 * Download certificate as JSON
 */
function downloadCertificate() {
    if (!currentSearchId) {
        alert('検索を実行してから証明書をダウンロードしてください');
        return;
    }

    window.location.href = '/api/certificate/' + currentSearchId;
}
