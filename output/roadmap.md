# Voice-Enabled Simulated Banking System Implementation Roadmap

### Step 1: Database Schema and Simulation API
Done when the system can perform CRUD operations on users, accounts, and transactions without voice involvement.
* Define SQLAlchemy models for `User`, `Account`, and `Transaction` (including status: pending/completed).
* Implement FastAPI endpoints to fetch balances, initiate transfers, and list recent bills.
* Create a seed script to populate the database with mock users and financial data.

### Step 2: Voice Biometric Authentication Module
Done when the system can verify a user's identity based on a provided audio sample.
* Implement an embedding generation function using a library like `speechbrain` or `torchaudio`.
* Create a cosine similarity check against stored voice embeddings.
* Expose a FastAPI endpoint to compare an incoming audio stream against a user’s registered voice vector.

### Step 3: Intent Recognition and Slot Filling (LangChain)
Done when the system can accurately parse voice transcriptions into structured JSON intents.
* Define LangChain prompts to extract "intent" (e.g., `transfer_money`), "amount", "recipient", and "bill_type".
* Implement a validator to ensure required slots are present before execution.

### Step 4: Transaction Orchestration (LangGraph)
Done when the system correctly manages the state machine for a multi-turn banking conversation.
* Design a LangGraph state schema to track: `authenticated`, `current_intent`, `pending_transaction_details`, and `history`.
* Implement nodes for: `Authenticate`, `ExtractIntent`, `ConfirmDetails`, and `ExecuteTransaction`.
* Configure conditional edges to loop back to the user if confirmation fails or if data is missing.

### Step 5: Voice I/O Integration Pipeline
Done when the system acts as a complete loop from raw audio in to synthetic audio out.
* Integrate a chosen STT library (e.g., OpenAI Whisper) to convert incoming audio to text.
* Integrate a TTS library (e.g., `gTTS` or `coqui-TTS`) to convert the final LangGraph response back into audio.
* Verify the end-to-end flow: User speaks -> Audio Transcribed -> Intent Resolved -> API Called -> Response Synthesized.