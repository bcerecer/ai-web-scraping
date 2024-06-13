# API Keys

1. Copy the `.env.template` file to `.env`:

   ```sh
   cp .env.template .env

2. Add your API keys in the `.env` file.

- **FIRECRAWL_API_KEY**: Retrieve from [Firecrawl Account](https://www.firecrawl.dev/account)
- **OPENAI_API_KEY**: Retrieve from [OpenAI API Keys](https://platform.openai.com/settings/profile?tab=api-keys)
- **RENTCAST_API_KEY**: Retrieve from [Rentcast API](https://app.rentcast.io/app/api)

# Run Script

1. **Create virtual environment**:
    ```sh
    python -m venv venv
    ```

2. **Activate virtual environment**:
    - On Windows:
        ```sh
        venv\Scripts\activate
        ```
    - On Unix or MacOS:
        ```sh
        source venv/bin/activate
        ```

3. **Install requirements**:
    ```sh
    pip install -r requirements.txt
    ```

4. **Run the script**:
    ```sh
    python ./app.py
    ```

# Output files

Raw data, formatted data and comparison CSV is saved in  `output/`

# Troubleshoot

If you encounter the error `An error occurred: BrowserType.launch`, you can resolve it by running:
```sh
playwright install
```