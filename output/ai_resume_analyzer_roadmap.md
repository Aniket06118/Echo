**Step 1: Resume Upload and Text Extraction**
*   **Done:** User can upload a PDF resume. The system successfully extracts all text content from the PDF.

**Step 2: Job Description Input and Keyword Extraction**
*   **Done:** User can input a job description as text. The system extracts key skills and keywords from the job description.

**Step 3: Resume Formatting Analysis**
*   **Done:** The system analyzes the extracted resume text for common formatting issues that can impact ATS readability, such as:
    *   Detection of text within headers and footers.
    *   Identification of tables, columns, or text boxes that might disrupt linear reading.
    *   Flagging of unusual characters, excessive use of special symbols, or non-standard fonts.

**Step 4: ATS Compatibility Check**
*   **Done:** The system assesses how well the resume's structure and content align with typical ATS parsing logic. This includes:
    *   Checking if crucial information (like contact details, work experience, education) is in clearly identifiable sections.
    *   Evaluating the consistency of formatting (e.g., date formats, section titles).
    *   Assessing the overall readability score based on the identified formatting elements.

**Step 5: Skills Gap and Keyword Matching**
*   **Done:** The system compares the skills and keywords identified in the resume against those extracted from the job description. It identifies skills present in the job description that are missing in the resume.

**Step 6: Score Calculation and Feedback Report**
*   **Done:** The system generates a compatibility score (e.g., 0-100%) based on keyword match percentage. A report is generated detailing:
    *   Percentage of matched keywords.
    *   A list of missing keywords from the job description.
    *   Specific formatting issues identified in Step 3.
    *   ATS compatibility feedback from Step 4.
    *   General suggestions for resume improvement.
