var yelpImages = function() {
    var starRatings = {
             0.0: '0.png',
             0.5: '0.png',
             1.0: '1.png',
             1.5: '1_half.png',
             2.0: '2.png',
             2.5: '2_half.png',
             3.0: '3.png',
             3.5: '3_half.png',
             4.0: '4.png',
             4.5: '4_half.png',
             5.0: '5.png'
         };
    var smallImagePath = "/foodbornemap/images/yelp-ratings-small/";
    var largeImagePath = "/foodbornemap/images/yelp-ratings-large/";

    function getImgNameFromRating(rating){
        return starRatings[Math.round(rating * 2) / 2];
    }

    return{
        getSmallImgFromRating: function(rating){
            return smallImagePath + getImgNameFromRating(rating);
        },

        getLargeImgFromRating: function(rating){
            return largeImagePath + getImgNameFromRating(rating);
        }
    }
}();

var reviewDisplay = function(){

    function displayReviews(reviewsDiv, reviews, sortFunction, sentenceDisplayFunction){
        reviews.sort(sortFunction);

        var reviewHtml = document.getElementById(reviewsDiv);
        reviewHtml.innerHTML = "";
        for(var i = 0; i < reviews.length; i++){
            var hsan = reviews[i]['classification_hsan'];

            let reviewDiv = document.createElement('div');
            reviewDiv.className = 'review-div';
            let date = getFormattedDate(new Date(reviews[i]['created']));

            let reviewHeader = document.createElement('div');
            reviewHeader.className = 'review-header';

            let container = document.createElement('div');
            container.className = "inner-container";

            container.appendChild(createYelpImg(reviews[i]['rating'], reviews[i]['url']));
            container.appendChild(createTextElement(date));
            reviewHeader.appendChild(container);

            container = document.createElement('div');
            container.className = 'inner-container';
            container.appendChild(createProgressElement(reviews[i]['classification']['total_score']));
            container.appendChild(createTextElement('LR'));

            var sentences = reviews[i]['text'].split(/(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s/);

            if(hsan && (sentences) && ("sentence_scores" in hsan)) {
                container.appendChild(createProgressElement(reviews[i]['classification_hsan']['total_score']));
                container.appendChild(createTextElement('HSAN'));
                reviewHeader.appendChild(container);
                reviewDiv.appendChild(reviewHeader);

                if(hsan['sentence_scores'].length == sentences.length) {
                    let sentencesDiv = sentenceDisplayFunction(hsan, sentences);
                    reviewDiv.appendChild(sentencesDiv);
                }
                else{
                    logSentencesDontMatch(reviews[i]['_id'], sentences.length, hsan['sentence_scores'].length)
                }
            }
            else{
                reviewHeader.appendChild(container);
                reviewDiv.appendChild(reviewHeader);
            }


            reviewHtml.appendChild(reviewDiv);
        }
    }

    function logSentencesDontMatch(reviewId, sentencesLength, HSANSentencesLength){
        $.post("/foodbornemap/log_sentence_error",
            {
                review_id: reviewId,
                sentences_split_length: sentencesLength,
                sentence_scores_length: HSANSentencesLength
            },
            function (result){}
            )
    }

    function displaySickSentences(hsan, sentences){
         let sickSentenceIndices = sentencesAboveThreshold(hsan['sentence_scores'], 0.5);
         let sentencesDiv = document.createElement('div');

         for(let i = 0; i < sickSentenceIndices.length; i++){
             let indexOfSickSentence = sickSentenceIndices[i];
             let sentenceInfo = createSentenceElement(sentences[indexOfSickSentence],
                 hsan['sentence_scores'][indexOfSickSentence], 'sentence-text-black', 'sentence-score-red');
             sentencesDiv.appendChild(sentenceInfo);
         }
         return sentencesDiv;
    }

    function displayAllSentences(hsan, sentences){
         let sickSentenceIndices = sentencesAboveThreshold(hsan['sentence_scores'], 0.5);
         let sentencesDiv = document.createElement('div');

         let counter = 0;
         for(let i = 0; i < sentences.length; i++){
             let sentenceInfo;
             if(counter < sickSentenceIndices.length && i == sickSentenceIndices[counter]){
                 counter++;
                 sentenceInfo = createSentenceElement(sentences[i], hsan['sentence_scores'][i], 'sentence-text-red', 'sentence-score-red');
             }
             else{
                 sentenceInfo = createSentenceElement(sentences[i], hsan['sentence_scores'][i], 'sentence-text-black', 'sentence-score-black');
             }
             sentencesDiv.appendChild(sentenceInfo);
         }
         return sentencesDiv;
    }

    function createSentenceElement(text, score, textClass, scoreClass){
         let sentenceInfo = document.createElement('div');
         sentenceInfo.className = 'sentence-info';

         let sentenceScore = document.createElement('div');
         sentenceScore.className = scoreClass;
         sentenceScore.textContent = score.toFixed(2);

         let revText = document.createElement('div');
         revText.className = textClass;
         revText.textContent = text;

         sentenceInfo.appendChild(sentenceScore);
         sentenceInfo.appendChild(revText);
         return sentenceInfo;
    }

    function createProgressElement(sickScore){
        let percentage = sickScore * 100;
        let fixedDecimal = sickScore.toFixed(2);

        let progressBar = document.createElement('div');
        progressBar.className= 'progress';
        let bar = document.createElement('div');
        bar.className = 'progress-bar bg-danger';
        bar.setAttribute('role', "progressbar");
        bar.setAttribute('aria-valuenow', "60");
        bar.setAttribute('aria-valuemin', "0");
        bar.setAttribute('aria-valuemax', "100");
        bar.setAttribute("style", "width: " + percentage + "%;");
        bar.textContent = fixedDecimal;

        progressBar.appendChild(bar);
        return progressBar;
    }

    function createTextElement(content) {
        let text = document.createElement('div');
        text.textContent = content;
        return text;
    }

    function createYelpImg(rating, url){
         let yelpDiv = document.createElement('div');
         let yelpLink = document.createElement('a');
         let yelpImg = document.createElement('img');
         yelpImg.src = yelpImages.getSmallImgFromRating(rating);
         yelpLink.href =  url;
         yelpLink.setAttribute("target", "_blank");
         yelpLink.appendChild(yelpImg);
         yelpDiv.appendChild(yelpLink);

         return yelpDiv;
    }

    function sentencesAboveThreshold(sentenceScores, threshold){
        let indices = [];
        let maxScore = sentenceScores[0];
        let maxIndex = 0;

        for(let i = 0; i< sentenceScores.length; i++){
            if (sentenceScores[i] >= threshold){
                indices.push(i);
            }
            else if (sentenceScores[i] > maxScore){
                maxScore = sentenceScores[i];
                maxIndex = i;
            }
        }
        if (indices.length > 0){
            return indices;
        }
        else{
            return [maxIndex];
        }
    }

    function compareReviews(field){
        return function(a, b) {
            var aScore;
            var bScore;
            if (field === 'created'){
                aScore = a[field];
                bScore = b[field];
            }
            else{
                aScore = a[field] ? a[field]['total_score']: 0;
                bScore = b[field]? b[field]['total_score']: 0;
            }
            return aScore < bScore ? 1 : -1
        }
    }

    return {
         displaySickReviews: function(reviewsDiv, reviews, field, allReviews=false){
             if(allReviews){
                 displayReviews(reviewsDiv, reviews, compareReviews(field), displayAllSentences);
             }
             else{
                 displayReviews(reviewsDiv, reviews, compareReviews(field), displaySickSentences);
             }
         }
    }

}();