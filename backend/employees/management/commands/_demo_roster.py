# main code
# Invented people over the real structure of the organigram DR-DI-03. The names below are
# generic combinations; no row comes from the real personnel file (11.2).

AF = 'Dir. Administrativa, Financiera y TI'
MP = 'Dir. Manufactura y Planeación'
MV = 'Dir. Mercadeo y Ventas'
OP = 'Dir. Operaciones'
PT = 'Dir. Procesos Técnicos'

# key, position, division, section, role, boss key
ROSTER = [
    ('gg', 'Gerente General', None, 'Gerencia', 'executive', None),
    ('gdn', 'Gerente de Desarrollo de Negocios', MV, 'Comercial', 'executive', 'gg'),
    ('d_op', 'Director(a) de Operaciones', OP, 'Ordenes de Producción', 'director', 'gg'),
    ('d_pt', 'Director(a) de Procesos Técnicos', PT, 'Procesos Técnicos', 'director', 'gg'),
    ('d_mp', 'Director(a) de Manufactura y Planeación', MP, 'Manufactura', 'director', 'gg'),
    ('d_af', 'Director(a) Administrativo, Financiero y TI', AF, 'Financiera', 'director', 'gg'),
    ('d_mv', 'Director(a) de Mercadeo y Ventas', MV, 'Comercial', 'director', 'gdn'),

    ('j_th', 'Jefe de Talento Humano', AF, 'Talento Humano', 'leader', 'd_af'),
    ('j_sos', 'Jefe de Sostenibilidad', AF, 'SGI', 'leader', 'd_af'),
    ('l_sst', 'Líder de Seguridad y Salud en el Trabajo', AF, 'SST', 'leader', 'j_sos'),
    ('l_cont', 'Líder de Contabilidad', AF, 'Financiera', 'leader', 'd_af'),
    ('l_ti', 'Líder de TI', AF, 'Tecnología', 'leader', 'd_af'),
    ('l_cost', 'Líder de Costos y Auditoría de Inventarios', AF, 'Financiera', 'leader', 'd_af'),
    ('a_nom', 'Analista de Nómina y Seguridad Social', AF, 'Talento Humano', 'analyst', 'j_th'),
    ('a_sgi', 'Analista SGI', AF, 'SGI', 'analyst', 'j_sos'),
    ('o_amb', 'Operario Oficios Varios Ambiental', AF, 'SST', 'operative', 'l_sst'),
    ('a_cont', 'Analista Contable', AF, 'Financiera', 'analyst', 'l_cont'),
    ('a_fin', 'Analista Financiero', AF, 'Financiera', 'analyst', 'l_cont'),
    ('a_ti1', 'Analista TI', AF, 'Tecnología', 'analyst', 'l_ti'),
    ('a_ti2', 'Analista TI', AF, 'Tecnología', 'analyst', 'l_ti'),
    ('a_cost', 'Analista de Costos', AF, 'Financiera', 'analyst', 'l_cost'),
    ('o_aud', 'Operario auditoria de inventarios', AF, 'Financiera', 'operative', 'l_cost'),

    ('j_pl', 'Jefe Planta', MP, 'Manufactura', 'leader', 'd_mp'),
    ('c_sp', 'Coordinador de Sección - Soldadura y Pintura', MP, 'Soldadura', 'leader', 'j_pl'),
    ('c_mc', 'Coordinador de Sección - Mecanizado y CDM', MP, 'Mecanizado y CDM', 'leader', 'j_pl'),
    ('c_oc', 'Coordinador Oxicorte y Corte', MP, 'Corte', 'leader', 'j_pl'),
    ('c_tal', 'Coordinador Taller', MP, 'Taller', 'leader', 'd_mp'),
    ('l_log', 'Líder de Logística', MP, 'Logística', 'leader', 'd_mp'),
    ('l_plan', 'Líder Planeación de Producción', MP, 'Programación de Producción', 'leader', 'd_mp'),
    ('o_sol1', 'Operario Soldador Básico (GMAW -SMAW)', MP, 'Soldadura', 'operative', 'c_sp'),
    ('o_sol2', 'Operario Soldador Básico (GMAW -SMAW)', MP, 'Soldadura', 'operative', 'c_sp'),
    ('o_sol3', 'Operario Soldador Formación (GMAW -SMAW)', MP, 'Soldadura', 'operative', 'c_sp'),
    ('o_pin', 'Operario Soldador Básico (GMAW -SMAW)', MP, 'Pintura', 'operative', 'c_sp'),
    ('o_cdm1', 'Operario CDM', MP, 'Mecanizado y CDM', 'operative', 'c_mc'),
    ('o_cdm2', 'Operario CDM - Experto', MP, 'Mecanizado y CDM', 'operative', 'c_mc'),
    ('o_cdm3', 'Operario CDM - Montador', MP, 'Ensamble', 'operative', 'c_mc'),
    ('o_tor1', 'Operario Torno', MP, 'Mecanizado y CDM', 'operative', 'c_mc'),
    ('o_tor2', 'Operario Torno y CDM', MP, 'Mecanizado y CDM', 'operative', 'c_mc'),
    ('o_cor1', 'Operario Corte', MP, 'Corte', 'operative', 'c_oc'),
    ('o_cor2', 'Operario Corte', MP, 'Oxicorte', 'operative', 'c_oc'),
    ('o_las', 'Operario Corte Láser', MP, 'Corte', 'operative', 'c_oc'),
    ('o_esm', 'Operario Corte', MP, 'Esmeriles', 'operative', 'c_oc'),
    ('o_for1', 'Operario Forja Básico', MP, 'Forja', 'operative', 'j_pl'),
    ('o_for2', 'Operario Forja Básico', MP, 'Forja', 'operative', 'j_pl'),
    ('o_cad', 'Operario Cadenas', MP, 'Cadenas', 'operative', 'j_pl'),
    ('o_tt1', 'Operario Tratamiento Térmico', MP, 'Planta de Tratamiento Térmico', 'operative', 'j_pl'),
    ('o_tt2', 'Operario Tratamiento Térmico', MP, 'Temple', 'operative', 'j_pl'),
    ('o_ban', 'Mecánico de Banco', MP, 'Taller', 'operative', 'c_tal'),
    ('o_con', 'Conductor', MP, 'Logística', 'operative', 'l_log'),
    ('o_desp', 'Auxiliar Almacén Despachos', MP, 'Despachos y Empaque', 'operative', 'l_log'),
    ('o_li', 'Operario Logística Interna - Proyectos', MP, 'Logística Interna', 'operative', 'l_log'),
    ('a_prog', 'Analista Programador de Producción', MP, 'Programación de Producción', 'analyst', 'l_plan'),
    ('a_ext', 'Analista Servicios Externos', MP, 'Servicios Externos', 'analyst', 'l_plan'),
    ('ap1', 'Aprendiz', MP, 'Soldadura', 'apprentice', 'c_sp'),
    ('ap2', 'Aprendiz', MP, 'Mecanizado y CDM', 'apprentice', 'c_mc'),
    ('ap3', 'Aprendiz', MP, 'Corte', 'apprentice', 'c_oc'),

    ('l_dis', 'Líder de Diseño', OP, 'Ingeniería', 'leader', 'd_op'),
    ('c_alm', 'Coordinador Almacenes', OP, 'Almacenes', 'leader', 'd_op'),
    ('c_op', 'Coordinador de Ordenes de Producción', OP, 'Ordenes de Producción', 'leader', 'd_op'),
    ('a_dib1', 'Analista Dibujante de Ingeniería', OP, 'Ingeniería', 'analyst', 'l_dis'),
    ('a_dib2', 'Analista Dibujante de Ingeniería', OP, 'Ingeniería', 'analyst', 'l_dis'),
    ('a_comp', 'Analista de Compras', OP, 'Cadena de Abastecimiento', 'analyst', 'd_op'),
    ('o_alm', 'Almacenista Producto Intermedio', OP, 'Almacenes', 'operative', 'c_alm'),
    ('a_op', 'Analista de Ordenes de Producción', OP, 'Ordenes de Producción', 'analyst', 'c_op'),

    ('l_cal', 'Líder de Calidad', PT, 'Calidad', 'leader', 'd_pt'),
    ('l_man', 'Líder de Mantenimiento y Mejora de Procesos', PT, 'Mantenimiento', 'leader', 'd_pt'),
    ('i_cal1', 'Inspector de Calidad', PT, 'Calidad', 'operative', 'l_cal'),
    ('i_cal2', 'Inspector de Calidad', PT, 'Calidad', 'operative', 'l_cal'),
    ('m_man1', 'Mecánico de Mantenimiento', PT, 'Mantenimiento', 'operative', 'l_man'),
    ('m_man2', 'Mecánico de Mantenimiento', PT, 'Mantenimiento', 'operative', 'l_man'),
    ('m_ele', 'Mecánico de Mantenimiento - Electricista', PT, 'Mantenimiento', 'operative', 'l_man'),
    ('o_loc', 'Oficial de Mantenimiento Locativo', PT, 'Mantenimiento', 'operative', 'l_man'),
    ('ing_st', 'Ingeniero Soporte Técnico Senior', PT, 'Procesos Técnicos', 'analyst', 'd_pt'),

    ('l_uen', 'Líder UEN', MV, 'Comercial', 'leader', 'd_mv'),
    ('e_com1', 'Ejecutivo Comercial', MV, 'Comercial', 'commercial', 'l_uen'),
    ('e_com2', 'Ejecutivo Comercial', MV, 'Comercial', 'commercial', 'l_uen'),
    ('e_com3', 'Ejecutivo Comercial', MV, 'Comercial', 'commercial', 'l_uen'),
    ('a_cn', 'Analista de Conexión de Negocios', MV, 'Marcas', 'analyst', 'gdn'),
]

FEMALE_NAMES = [
    'Ana María', 'Laura', 'Valentina', 'Daniela', 'Catalina', 'Paula Andrea', 'Luisa Fernanda',
    'Sara', 'Manuela', 'Juliana', 'Carolina', 'Natalia', 'Marcela', 'Yuliana', 'Diana Patricia',
    'Sandra Milena', 'Luz Adriana', 'Mónica', 'Isabel', 'Alejandra',
]

MALE_NAMES = [
    'Juan Camilo', 'Santiago', 'Andrés Felipe', 'Carlos Mario', 'Jhon Fredy', 'Sebastián',
    'Mateo', 'Julián', 'Esteban', 'Diego Alejandro', 'Jorge Iván', 'Luis Fernando', 'Óscar',
    'Wilson', 'Hernán', 'Cristian David', 'Felipe', 'Mauricio', 'Alexander', 'Daniel',
]

SURNAMES = [
    'Restrepo', 'Gómez', 'Zapata', 'Ospina', 'Arango', 'Vélez', 'Montoya', 'Cardona', 'Giraldo',
    'Múnera', 'Henao', 'Echeverri', 'Posada', 'Mejía', 'Londoño', 'Agudelo', 'Álvarez',
    'Betancur', 'Quintero', 'Correa', 'Castaño', 'Sierra', 'Hoyos', 'Palacio', 'Duque',
    'Arboleda', 'Toro', 'Uribe', 'Mesa', 'Bedoya',
]

CITIES = ['Medellín', 'Itagüí', 'Envigado', 'Bello', 'Sabaneta', 'La Estrella']

NEIGHBORHOODS = [
    'Belén', 'Laureles', 'Robledo', 'Castilla', 'Manrique', 'Buenos Aires', 'San Javier',
    'Santa María', 'Ditaires', 'Niquía', 'La Tablaza', 'Calatrava', 'San Antonio de Prado',
    'Zona Centro', 'Las Vegas',
]

COLOMBIAN_BIRTHPLACES = [
    'Medellín', 'Rionegro', 'Caldas', 'Apartadó', 'Santa Rosa de Osos', 'Yarumal', 'Montería',
    'Quibdó', 'Cali', 'Bogotá', 'Manizales', 'Andes', 'Turbo', 'Sonsón',
]

VENEZUELAN_BIRTHPLACES = ['Maracaibo', 'Valencia', 'Barquisimeto', 'Caracas']

DEGREES = {
    'bachelor': ['Bachiller Académico', 'Bachiller Técnico Industrial'],
    'technical': [
        'Técnico en Soldadura', 'Técnico en Mecanizado CNC', 'Técnico en Mantenimiento Eléctrico',
        'Técnico en Logística',
    ],
    'technologist': [
        'Tecnología en Mecánica Industrial', 'Tecnología en Gestión Logística',
        'Tecnología en Control de Calidad', 'Tecnología en Análisis y Desarrollo de Software',
    ],
    'professional': [
        'Ingeniería Mecánica', 'Ingeniería Industrial', 'Administración de Empresas',
        'Contaduría Pública', 'Psicología', 'Ingeniería de Sistemas', 'Ingeniería Metalúrgica',
        'Negocios Internacionales',
    ],
    'postgraduate': [
        'Especialización en Gerencia de Proyectos', 'Especialización en Gestión Humana',
        'Especialización en Finanzas', 'Especialización en Seguridad y Salud en el Trabajo',
    ],
    'masters': ['Maestría en Administración (MBA)', 'Maestría en Ingeniería'],
}

NOTES = [
    'Restricción médica temporal: no levantar más de 15 kg hasta diciembre de 2026.',
    'Pendiente entregar copia actualizada del certificado de estudios.',
    'Contrato próximo a vencer: definir renovación con el jefe inmediato.',
    'Solicitó cambio de turno por estudios nocturnos.',
    'Reintegro tras incapacidad prolongada; seguimiento de SST mensual.',
    'Tiene embargo de nómina vigente.',
    'Postulado a plan de carrera como coordinador de sección.',
    'Vacaciones acumuladas de dos periodos.',
]
