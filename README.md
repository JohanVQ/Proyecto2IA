# Proyecto_IA2
Segundo proyecto del curso de Inteligencia artificial, basado en un agente que resuelve el juego Buscaminas por medio de inferencia.

**Descripción del problema:** 
Se requiere resolver el juego de buscaminas utilizando un agente de inteligencia artificial, utilizando lógica de primer nivel e inferencia.
El juego de buscaminas consiste en un tablero con una determinada cantidad de celdas (Varía según la dificultad seleccionada por el jugador) las cuales pueden contener o no una mina. El juego se soluciona revelando todas las celdas seguras de la partida sin "pisar" una mina en el proceso. Cuando se revela una de las celdas esta puede ser una mina o una celda segura, si es segura entonces ella provee información numérica de cuantas minas se encuentran en las celdas de su alrededor. Si la celda revelada tiene un valor de 0, las celdas vecinas se revelan automáticamente. El juego se pierde si se pisa una mina. A continuación un ejemplo de como se visualiza el tablero:

1  1  1  □  □
1  *  2  □  □
1  1  2  1  1
□  □  1  * 1
□  □  1  1  1

**Lógica implementada para la inferencia:** 
Para determinar nueva información se hizo uso de una lógica distinta a la vista en clases. En este caso, en lugar de usar símbolos y operaciones lógicas, se utilizan operaciones númericas y de conjuntos. El agente tiene dos formas básicas de recolectar información, señalar las celdas que son minas aseguradas según la información de las celdas y señalar las celdas seguras mediante el mismo método. Esto se logra fácilmente a partir del conteo de las celdas vecinas y comparandolas con el número de minas establecido por la celda actual, por ejemplo:

□  2  □
1  2  1 ==> Una situación como esta el sistema la interpreta como dos minas aseguradas, ya que el número de casillas sin descubrir esel mismo que el conteo de minas.
1  2  1

Se sigue exactamente la misma lógica para el trackeo de celdas seguras. Es decir, cuando el número n de celdas sin revelar es igual al número x de minas o celdas seguras, eso da pie a que el sistema pueda interpretar esa información.
Una vez el sistema tiene estas funciones, es capaz de crear sentencias del tipo [(3,2),(3,3),(3,4)] = 2. Donde se establece la cantidad de minas que se pueden contar dentro de un conjunto determinado de celdas. Todas estas funciones son las que nos permiten crear lo que conocemos como **knowledge base**.
Una vez agregada la información al knowledge base, es posible empezar a crear información por medio de inferencia. En este caso, la forma en la que se crea nueva información es bastante natural y hasta cierto punto intuitiva. Cuando se tienen dos sentencias que repiten una cierta cantidad de celdas, siendo que las sentencias tiene una estructura ([celdas], cantidad_minas), entonces es posible determinar mediante una resta el número de minas que tiene el subconjunto del conjunto más grande en la comparación. Esto se logra comparando todas las sentencias dentro del knowledge base para generar sentencias completamente nuevas. El ejemplo siguiente explica como funciona el proceso descrito.
Sentencia 1 ==> {[(3,2), (3, 3), (3, 4)], 2}
sentencia 2 ==> {[(3,2), (3, 3), (3, 4), (4,2), (4, 3), (4, 4)], 5}
Sentencia 3 ==> Setencia 1 - Sentencia 2 ==> {[(4,2), (4, 3), (4, 4)], 3} ==> Se resta la cantidad de minas y se conservan únicamente las celdas que no pertenencen a ambas sentencias.
De esta manera se logró determinar una sentencia 3 completamente nueva que puede seguir alimentando de información el conocimiento del agente.

**Flujo del agente:**
1. Añadir conocimiento: Establece el valor de la celda actual y crea las sentencias que se puedan.
2. Actualizar el conocimiento: Toma las sentencias creadas y determina las minas y posiciones seguras que se puedan inferir únicamente con el estado de ese conjunto.
3. Inferencia de nuevas sentencias: Propone nuevas sentencias utilizando las que ya estan dentro del knowledge base, por medio del proceso anteriormente descrito.
4. Actualizar nuevamente: Se deben volver a determinar las minas y posiciones seguras posibles, ya que el proceso de inferencia pudo haber agregado nuevas sentencias.

**Retos afrontados:**
Entre los retos afrontados en el desarrollo del proyecto podemos identificar:
1. Investigación de nuevas formas de inferencia, con diferentes métodos y componentes que los vistos en clases.
2. Aunque no se haya usado el módelo lógico desarrollado en clases, fue necesario explorar esta posibilidad para entender en que fallaba y cual era el rumbo que necesitabamos seguir para resolver el problema.
3. Fue necesario tener una alta comprensión de los conceptos clave del tema tratado, inferencia y lógica de primer orden. Esto debido a que hay múltiples maneras de solucionar este problema, utilizando métodos que no se apegan realmente a lo visto en las lecciones. Por lo que debíamos ser capaces de filtrar dicha información para llegar a una alternativa válida para el propósito del proyecto.
4. Finalmente fue necesario algo de esfuerzo para poder integrar la lógica investigada dentro del proyecto. Sobretodo pensar en como se desarrollan las iteraciones del agente.

**Integrantes:**
Johan Vargas
Fabián Villalobos

**Conclusiones finales:**
El proyecto fue entretenido de desarrollar, fue un buen acercamiento a las diferentes formas que puede tomar la inferencia. Es interesante ver como un concepto o metodología puede aplicarse de manera diferente dependiendo del escenario y como de una manera funciona de forma eficiente y de otra forma es casi imposible de implementar, siendo que se esta usando inferencia en ambas aproximaciones. Creemos que el proyecto permitió que nos envolvieramos apropiadamente de la información investigada y que pudieramos enfocarnos en la parte importante del proyecto, sin perder tiempo en tareas repetitivas que ya hemos desarrollado en cursos pasados.
