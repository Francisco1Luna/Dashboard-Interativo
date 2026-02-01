import pandas as pd
import streamlit as st
import plotly.express as px
import pycountry

#criar texto de titulo, emoji e layout da aplicação
st.set_page_config(
    page_title='Darshboar Interativo de Salarios na Área de Dados',
    page_icon='🛢',
    layout='wide'
)

#carregamentos de dados
df=pd.read_csv('https://raw.githubusercontent.com/guilhermeonrails/data-jobs/refs/heads/main/salaries.csv')

#limpar dados nulos
df_limpo=df.dropna()

#corrijir tipo de dado do ano float64-->int64
df_limpo = df_limpo.assign(work_year = df_limpo['work_year'].astype('Int64'))

#correçao dados remotos
rename_remote = {
    0 : 'presencial',
    100 : 'home office',
    50 : 'vagas hibridas',
}
df['remote_ratio'] = df['remote_ratio'].map(rename_remote)  

#correçao dos nomes senioridade
renomear_senioridades=({
    'EN': 'junior',
    'MI': 'pleno' ,
    'SE': 'senior',
    'EX': 'executivo'
})
df_limpo['experience_level']=df_limpo['experience_level'].map(renomear_senioridades)

#correçao tipos de contratos
renomear_contratos=({
    'FT': 'tempo integral',
    'CT': 'contrato',
    'PT': 'meio periodo',
    'FL': 'freelance'
})

df_limpo['employment_type']=df_limpo['employment_type'].map(renomear_contratos)

#correçao tamanho da empresa
renomear_tamanho=({
    'S': 'pequena',
    'M': 'media',
    'L': 'grande',
})
df_limpo['company_size']=df_limpo['company_size'].map(renomear_tamanho)


#criaçao da barra lateral(filtros)
st.sidebar.header('🔍Filtros')

#filtros de anos
anos_disponiveis=sorted(df_limpo['work_year'].unique())
anos_selecionados=st.sidebar.multiselect('Ano🗓️', anos_disponiveis, default=anos_disponiveis)

#filtros de senioridade
senioridades_disponiveis=sorted(df_limpo['experience_level'].unique())
senioridades_selecionadas=st.sidebar.multiselect('Senioridades📊',senioridades_disponiveis,default=senioridades_disponiveis)

#filtro por tipos de contratos
contratos_disponiveis=sorted(df_limpo['employment_type'].unique())
contratos_selecionados=st.sidebar.multiselect('Contratos📝',contratos_disponiveis,default=contratos_disponiveis)

#filtro por tamanho da empresa
empresas_disponiveis=sorted(df_limpo['company_size'].unique())
empresas_selecionadas=st.sidebar.multiselect('Tamanho da Empresa📈',empresas_disponiveis,default=empresas_disponiveis)

#filtragem do df inicial com base nas seleçoes da barra lateral
df_filtrado=df_limpo[
    (df_limpo['work_year'].isin(anos_selecionados))&
    (df_limpo['experience_level'].isin(senioridades_selecionadas))&
    (df_limpo['employment_type'].isin(contratos_selecionados))&
    (df_limpo['company_size'].isin(empresas_selecionadas))
]
#conteudo principal
st.title('👨‍💻Dashboard de Ánalise de Salarios na Área Dados👨‍💻')
st.markdown('Explore os dados salariais na área de dados nos ultimos anos. Utilize a ajuda dos filtros na esquerda para navegar melhor')

#metricas principais
st.subheader('Metricas gerais(salario anual em dólares)')

if not df_filtrado.empty:
    salario_medio=df_filtrado['salary_in_usd'].mean()
    salario_maximo=df_filtrado['salary_in_usd'].max()
    total_registros=df_filtrado.shape[0]
    cargo_mais_registrado=df_filtrado['job_title'].mode()[0]
else:
    salario_medio,salario_maximo,total_registros,cargo_mais_registrado=0,0,0, ''
#fazer as colunas e atribuir valor a elas
col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário médio", f"${salario_medio:,.0f}")
col2.metric("Salário máximo", f"${salario_maximo:,.0f}")
col3.metric("Total de registros", f"{total_registros:,}")
col4.metric("Cargo mais frequente", cargo_mais_registrado)

st.markdown('---')

#criaçao dos graficos

col_graf1,col_graf2= st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_cargos=df_filtrado.groupby('job_title')['salary_in_usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos=px.bar(
        top_cargos,
        x='salary_in_usd',
        y='job_title',
        orientation='h',    
        title='Top 10 cargos por salario médio',
        labels= {'salary_in_usd': 'Média de salario anual em dólares','job_title':'Cargos'}
        )
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        st.warning('Nenhum dado encontrado')   
with col_graf2:
    if not df_filtrado.empty:
        grafico_hist=px.histogram (
        df_filtrado,
        x='salary_in_usd',
        nbins=30,
        title=30,
        labels={'salary_in_usd':'salario em dólares', 'count': ''}
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist,use_container_width=True)
    else:
        st.warning('Nenhum dado para exibir')
col_graf3, col_graf4= st.columns(2)
with col_graf3:
    if not df_filtrado.empty:
            remoto_contagem=df_filtrado['remote_ratio'].value_counts().reset_index()    
            remoto_contagem.columns=['remote_ratio','quantidade']
            grafico_remoto=px.pie(
            remoto_contagem,
            names='remote_ratio',
            values='quantidade',
             title='proporção dos tipos de trabalho',
             hole=0.5
             )
            grafico_remoto.update_traces(textinfo='percent+label')
            grafico_remoto.update_layout(title_x=0.1)
            st.plotly_chart(grafico_remoto,use_container_width=True)
    else:
        st.warning('Nenhum dado para exibir')


#funcao para converter iso 2 para iso 3
def iso_2_to_iso3(code):
    if not isinstance(code, str):
        return None
    try:
        return pycountry.countries.get(alpha_2=code.strip().upper()).alpha_3
    except:
        return None


#criar nova coluna com codigo iso_3
df_limpo['residencia_iso3']=df_limpo['employee_residence'].apply(iso_2_to_iso3)

#calcular media salarial por país
df_ds=df_limpo[df_limpo['job_title']=='Data Scientist']
df_ds['residencia_iso3'] = df_ds['employee_residence'].apply(iso_2_to_iso3)
media_ds_pais=df_ds.groupby('residencia_iso3')['salary_in_usd'].mean().reset_index()

with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['job_title'] == 'Data Scientist']
        df_ds['residencia_iso3'] = df_ds['employee_residence'].apply(iso_2_to_iso3)
        media_ds_pais = df_ds.groupby('residencia_iso3')['salary_in_usd'].mean().reset_index()
        grafico_paises = px.choropleth(media_ds_pais,
            locations='residencia_iso3',
            color='salary_in_usd',
            color_continuous_scale='rdylgn',
            title='Salário médio de Cientista de Dados por país',
            labels={'salary_in_usd': 'Salário médio (USD)', 'residencia_iso3': 'País'})
        grafico_paises.update_layout(title_x=0.1)
        st.plotly_chart(grafico_paises, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de países.")

#tabela de dados detalhados
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)
st.markdown('---')
st.markdown('Feito por: Francisco Luna de Moraes com a ajuda da https://www.alura.com.br/promocao/awin_10EstudeAlurax?utm_source=awin&utm_medium=site&utm_term=1042425&utm_id=gx-br-awin-alura-ssd&aw_affid=1042425&awc=23465_1769809888_f319c3858311f434cbef346a93d7fe01')     
print(df_limpo.head())
   