using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Networking;
using System.Collections;
using System.Text;

// --- Estruturas de Dados para a API (JSON) ---
[System.Serializable] public class LoginData { public string apelido; public string senha; }
[System.Serializable] public class AlunoData { public string id; public string nome; public int pontuacao_total; }
[System.Serializable] public class ApiResponse { public string status; public string mensagem; public AlunoData dados_aluno; }

public class LoginBuilder : MonoBehaviour
{
    // --- Configuração da API ---
    private const string baseUrl = "http://127.0.0.1:5000"; // Mude para a URL do Render em produção

    // --- Referências da Cena ---
    // A única coisa que precisamos arrastar no Inspector é o Canvas principal.
    public Canvas mainCanvas;

    // --- Referências dos Elementos de UI Criados via Código ---
    private GameObject loginPanel;
    private InputField apelidoInput;
    private InputField senhaInput;
    private Button loginButton;
    private Text statusText;

    private GameObject welcomePanel;
    private Text welcomeText;

    void Start()
    {
        if (mainCanvas == null)
        {
            Debug.LogError("O Canvas principal não foi atribuído no Inspector!");
            return;
        }

        // Inicia a construção da interface
        BuildLoginUI();
        BuildWelcomeUI();

        // Garante que apenas a tela de login esteja visível no início
        welcomePanel.SetActive(false);
    }

    #region Construtores de UI

    private void BuildLoginUI()
    {
        // --- 1. Cria o Painel Principal ---
        loginPanel = CreatePanel("LoginPanel", mainCanvas.transform);

        // --- 2. Cria o Título ---
        Text title = CreateText("Title", loginPanel.transform, "Detetives do Parque", 40, TextAnchor.MiddleCenter);
        SetRectTransform(title.rectTransform, new Vector2(0.5f, 0.85f), new Vector2(0.5f, 0.85f), new Vector2(0.5f, 0.5f), new Vector2(400, 100));

        // --- 3. Cria os Campos de Input ---
        apelidoInput = CreateInputField("ApelidoInput", loginPanel.transform, "Digite seu apelido...");
        SetRectTransform(apelidoInput.GetComponent<RectTransform>(), new Vector2(0.5f, 0.6f), new Vector2(0.5f, 0.6f), new Vector2(0.5f, 0.5f), new Vector2(300, 50));

        senhaInput = CreateInputField("SenhaInput", loginPanel.transform, "Digite sua senha...");
        senhaInput.contentType = InputField.ContentType.Password;
        SetRectTransform(senhaInput.GetComponent<RectTransform>(), new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(300, 50));

        // --- 4. Cria o Botão de Login ---
        loginButton = CreateButton("LoginButton", loginPanel.transform, "Entrar");
        loginButton.onClick.AddListener(OnLoginButtonClicked); // Adiciona a função ao clique
        SetRectTransform(loginButton.GetComponent<RectTransform>(), new Vector2(0.5f, 0.35f), new Vector2(0.5f, 0.35f), new Vector2(0.5f, 0.5f), new Vector2(200, 60));

        // --- 5. Cria o Texto de Status ---
        statusText = CreateText("StatusText", loginPanel.transform, "", 18, TextAnchor.MiddleCenter);
        statusText.color = Color.red;
        SetRectTransform(statusText.rectTransform, new Vector2(0.5f, 0.25f), new Vector2(0.5f, 0.25f), new Vector2(0.5f, 0.5f), new Vector2(300, 40));
    }
    
    private void BuildWelcomeUI()
    {
        // --- 1. Cria o Painel de Boas-Vindas ---
        welcomePanel = CreatePanel("WelcomePanel", mainCanvas.transform);

        // --- 2. Cria o Texto de Boas-Vindas ---
        welcomeText = CreateText("WelcomeText", welcomePanel.transform, "Bem-vindo!", 30, TextAnchor.MiddleCenter);
        SetRectTransform(welcomeText.rectTransform, new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(400, 200));
    }

    #endregion

    #region Lógica da API

    public void OnLoginButtonClicked()
    {
        StartCoroutine(LoginCoroutine(apelidoInput.text, senhaInput.text));
    }

    private IEnumerator LoginCoroutine(string apelido, string senha)
    {
        statusText.text = "Entrando...";
        loginButton.interactable = false;

        LoginData data = new LoginData { apelido = apelido, senha = senha };
        string jsonBody = JsonUtility.ToJson(data);
        string url = baseUrl + "/login";

        using (UnityWebRequest webRequest = new UnityWebRequest(url, "POST"))
        {
            byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonBody);
            webRequest.uploadHandler = new UploadHandlerRaw(bodyRaw);
            webRequest.downloadHandler = new DownloadHandlerBuffer();
            webRequest.SetRequestHeader("Content-Type", "application/json");

            yield return webRequest.SendWebRequest();

            if (webRequest.result != UnityWebRequest.Result.Success)
            {
                statusText.text = "Erro de conexão.";
                Debug.LogError("Erro na requisição: " + webRequest.error);
            }
            else
            {
                ApiResponse response = JsonUtility.FromJson<ApiResponse>(webRequest.downloadHandler.text);
                if (response.status == "sucesso")
                {
                    ShowWelcomeScreen(response.dados_aluno.nome);
                }
                else
                {
                    statusText.text = response.mensagem;
                }
            }
        }
        loginButton.interactable = true;
    }

    private void ShowWelcomeScreen(string nomeAluno)
    {
        loginPanel.SetActive(false);
        welcomePanel.SetActive(true);
        welcomeText.text = $"Bem-vindo, detetive\n{nomeAluno}!";
    }

    #endregion

    #region Funções Auxiliares de UI (Helpers)

    // Estas funções ajudam a criar os elementos para não repetir código.
    private GameObject CreatePanel(string name, Transform parent)
    {
        GameObject panel = new GameObject(name, typeof(RectTransform), typeof(Image));
        panel.transform.SetParent(parent, false);
        panel.GetComponent<Image>().color = new Color(0.1f, 0.1f, 0.1f, 0.5f); // Cor escura semi-transparente
        SetRectTransform(panel.GetComponent<RectTransform>(), Vector2.zero, Vector2.one, new Vector2(0.5f, 0.5f), Vector2.zero);
        return panel;
    }

    private Text CreateText(string name, Transform parent, string content, int fontSize, TextAnchor alignment)
    {
        GameObject textGO = new GameObject(name, typeof(RectTransform), typeof(Text));
        textGO.transform.SetParent(parent, false);
        Text text = textGO.GetComponent<Text>();
        text.text = content;
        text.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
        text.fontSize = fontSize;
        text.color = Color.white;
        text.alignment = alignment;
        return text;
    }

    private InputField CreateInputField(string name, Transform parent, string placeholder)
    {
        // InputField precisa de uma imagem de fundo e um texto para o conteúdo/placeholder
        GameObject inputGO = new GameObject(name, typeof(RectTransform), typeof(Image), typeof(InputField));
        inputGO.transform.SetParent(parent, false);
        
        Image img = inputGO.GetComponent<Image>();
        img.color = new Color(1, 1, 1, 0.1f);

        InputField input = inputGO.GetComponent<InputField>();
        
        Text placeholderText = CreateText("Placeholder", inputGO.transform, placeholder, 20, TextAnchor.MiddleLeft);
        placeholderText.color = Color.gray;
        placeholderText.fontStyle = FontStyle.Italic;
        RectTransform placeholderRect = placeholderText.rectTransform;
        placeholderRect.anchorMin = new Vector2(0, 0);
        placeholderRect.anchorMax = new Vector2(1, 1);
        placeholderRect.offsetMin = new Vector2(10, 0);
        placeholderRect.offsetMax = new Vector2(-10, 0);

        Text inputText = CreateText("Text", inputGO.transform, "", 20, TextAnchor.MiddleLeft);
        RectTransform textRect = inputText.rectTransform;
        textRect.anchorMin = new Vector2(0, 0);
        textRect.anchorMax = new Vector2(1, 1);
        textRect.offsetMin = new Vector2(10, 0);
        textRect.offsetMax = new Vector2(-10, 0);

        input.placeholder = placeholderText;
        input.textComponent = inputText;
        return input;
    }

    private Button CreateButton(string name, Transform parent, string label)
    {
        GameObject buttonGO = new GameObject(name, typeof(RectTransform), typeof(Image), typeof(Button));
        buttonGO.transform.SetParent(parent, false);
        
        Text labelText = CreateText("Label", buttonGO.transform, label, 24, TextAnchor.MiddleCenter);
        labelText.color = Color.black;

        return buttonGO.GetComponent<Button>();
    }

    private void SetRectTransform(RectTransform rt, Vector2 anchorMin, Vector2 anchorMax, Vector2 pivot, Vector2 sizeDelta)
    {
        rt.anchorMin = anchorMin;
        rt.anchorMax = anchorMax;
        rt.pivot = pivot;
        rt.sizeDelta = sizeDelta;
        rt.anchoredPosition = Vector2.zero;
    }

    #endregion
}
