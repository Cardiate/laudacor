const express = require('express');
const cors = require('cors');
const path = require('path');
const { OpenAI } = require('openai'); // Biblioteca da OpenAI

const app = express();
app.use(cors());
app.use(express.json());

// Serve os arquivos estáticos (index.html, logo.png)
app.use(express.static(__dirname));

// Variável temporária na memória do servidor (APENAS PARA TESTE LOCAL)
let chaveApiTemporaria = "";

// Rota para salvar a chave (Teste local)
app.post('/api/usuarios/api-key', (req, res) => {
    const { apiKey } = req.body;
    chaveApiTemporaria = apiKey; // Salva na memória
    console.log("Chave recebida para teste local!");
    res.status(200).json({ success: true });
});

// Rota para gerar o laudo com IA
app.post('/api/ia/gerar-laudo', async (req, res) => {
    try {
        if (!chaveApiTemporaria) {
            return res.status(400).json({ error: "Chave da OpenAI não configurada. Vá na aba Configurações." });
        }

        const dados = req.body;

        // Inicializa o cliente da OpenAI com a chave salva temporariamente
        const openai = new OpenAI({
            apiKey: chaveApiTemporaria,
        });

        // O Prompt que diz à IA como ela deve se comportar
        const systemPrompt = `Você é um médico cardiologista experiente escrevendo um laudo de angiotomografia de coronárias (Método AHA 17 Segmentos). 
Escreva um texto formal, em português, dividido em parágrafos. 
Primeiro, descreva a técnica do exame. 
Depois, descreva os achados nas artérias (use o nome das artérias e as porcentagens de lesão fornecidas). 
Por fim, emita uma conclusão diagnóstica. Não invente lesões que não estejam no JSON.`;

        // O JSON com os dados do paciente e as lesões
        const userPrompt = `Gere o laudo médico com base nestes achados angiográficos:\n\n${JSON.stringify(dados, null, 2)}`;

        // Chamada para a API da OpenAI
        const response = await openai.chat.completions.create({
            model: "gpt-4o-mini", // Modelo rápido e barato (pode usar gpt-4o também)
            messages: [
                { role: "system", content: systemPrompt },
                { role: "user", content: userPrompt }
            ],
            temperature: 0.4, // Texto mais técnico e menos "criativo"
        });

        // Pega o texto gerado
        const textoLaudo = response.choices[0].message.content;
        
        // Envia de volta para o frontend
        res.status(200).json({ textoLaudo });

    } catch (error) {
        console.error("Erro ao chamar OpenAI:", error.response ? error.response.data : error.message);
        res.status(500).json({ error: "Falha ao gerar o laudo pela IA." });
    }
});

// Inicia o servidor
const PORT = process.env.PORT || 3001; // Use a porta que estava funcionando aí (3000, 3001 ou 4545)
app.listen(PORT, () => {
    console.log(`Servidor rodando na porta ${PORT}`);
});
